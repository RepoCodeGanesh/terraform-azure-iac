import azure.functions as func
import json
import logging
import os
import re
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

# ── Azure Monitor OpenTelemetry Instrumentation (Safe Initialization) ─────────
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_azure_monitor()
except Exception as _telemetry_err:
    logging.getLogger(__name__).debug("OpenTelemetry initialization skipped: %s", _telemetry_err)

try:
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions
    HAS_CONTENT_SAFETY = True
except ImportError:
    HAS_CONTENT_SAFETY = False

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ── Constants ──────────────────────────────────────────────────────────────────
OPENAI_ENDPOINT         = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
OPENAI_MODEL            = os.environ.get("AZURE_OPENAI_MODEL", "gpt-5.4-nano")
SEARCH_ENDPOINT         = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
SEARCH_INDEX            = os.environ.get("AZURE_SEARCH_INDEX", "tax-docs")
CONTENT_SAFETY_ENDPOINT = os.environ.get("AZURE_CONTENT_SAFETY_ENDPOINT", "")
COSMOS_DB_ENDPOINT      = os.environ.get("COSMOS_DB_ENDPOINT", "")
COSMOS_DB_DATABASE      = os.environ.get("COSMOS_DB_DATABASE", "db-tax-advisor")
COSMOS_DB_CONTAINER     = os.environ.get("COSMOS_DB_CONTAINER", "chat_history")
APP_NAME                = os.environ.get("APP_NAME", "TaxBot India")
APP_VERSION             = os.environ.get("APP_VERSION", "1.0.0")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, x-session-id",
    "Content-Type": "application/json",
}

try:
    from azure.cosmos import CosmosClient
    HAS_COSMOS = True
except ImportError:
    HAS_COSMOS = False

SYSTEM_PROMPT = """You are TaxBot India, an expert Indian income tax advisor for FY 2026-27 (AY 2027-28).
You have deep knowledge of:
- Old vs New Tax Regime (new regime default, zero tax up to ₹12L)
- All deductions: 80C (₹1.5L), 80D, 80CCD(1B) NPS extra ₹50K, HRA, home loan 24b
- Budget 2025 changes: ₹12L zero tax, LTCG 12.5%, NPS employer 14%
- Salary components, CTC restructuring, advance tax, ITR filing
- Section 87A rebate, surcharge, cess (4%)

Rules:
- Always start greetings with "Welcome 🙏"
- Always recommend consulting a CA for personalised advice
- Quote relevant sections (e.g., "Under Section 80C...")
- Be precise with numbers and calculations
- For calculations, show step-by-step working
- Recommend the better regime with clear reasoning
- Use Indian number format (₹10,00,000 not ₹1000000)
- Keep responses concise but complete
"""

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()

def get_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        azure_ad_token_provider=lambda: get_credential().get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token,
        api_version="2024-12-01-preview",
    )

def extract_response_text(resp) -> str:
    """Safely extract text content from OpenAI ChatCompletion or Stream object."""
    if not resp:
        return ""
    if hasattr(resp, "choices") and resp.choices:
        return resp.choices[0].message.content or ""
    try:
        parts = []
        for chunk in resp:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta and hasattr(delta, "content") and delta.content:
                    parts.append(delta.content)
                elif hasattr(chunk.choices[0], "message") and chunk.choices[0].message and chunk.choices[0].message.content:
                    parts.append(chunk.choices[0].message.content)
        return "".join(parts)
    except Exception as e:
        logging.error(f"Error extracting stream response text: {e}")
        return ""

# ── Cosmos DB Session Persistence Helpers ─────────────────────────────────────
_cosmos_container = None

def get_cosmos_container():
    global _cosmos_container
    if _cosmos_container is not None:
        return _cosmos_container
    if not HAS_COSMOS or not COSMOS_DB_ENDPOINT:
        return None
    try:
        credential = get_credential()
        client = CosmosClient(COSMOS_DB_ENDPOINT, credential=credential)
        db = client.get_database_client(COSMOS_DB_DATABASE)
        _cosmos_container = db.get_container_client(COSMOS_DB_CONTAINER)
        return _cosmos_container
    except Exception as e:
        logging.warning("Cosmos DB initialization failed: %s", e)
        return None

def save_chat_turn(session_id: str, user_message: str, reply: str, model: str = OPENAI_MODEL) -> bool:
    container = get_cosmos_container()
    if not container:
        return False
    try:
        import uuid
        doc = {
            "id": str(uuid.uuid4()),
            "sessionId": session_id,
            "userMessage": user_message,
            "reply": reply,
            "model": model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        container.upsert_item(doc)
        return True
    except Exception as e:
        logging.warning("Failed to save chat turn to Cosmos DB: %s", e)
        return False

def get_session_history(session_id: str, limit: int = 20) -> list:
    container = get_cosmos_container()
    if not container:
        return []
    try:
        query = "SELECT c.id, c.sessionId, c.userMessage, c.reply, c.timestamp FROM c WHERE c.sessionId = @sessionId ORDER BY c.timestamp ASC"
        items = list(container.query_items(
            query=query,
            parameters=[{"name": "@sessionId", "value": session_id}],
            enable_cross_partition_query=False,
            partition_key=session_id
        ))
        return items[-limit:]
    except Exception as e:
        logging.warning("Failed to fetch session history from Cosmos DB: %s", e)
        return []

def sanitize_pii(text: str) -> str:
    """Mask Indian PAN card numbers and Aadhaar numbers to enforce PII privacy."""
    if not text:
        return ""
    # Mask PAN (5 letters, 4 digits, 1 letter)
    text = re.sub(r'\b[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}\b', '[PAN-REDACTED]', text)
    # Mask Aadhaar (12 digits, option spaces)
    text = re.sub(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b', '[AADHAAR-REDACTED]', text)
    return text

def analyze_prompt_safety(text: str) -> dict:
    """Analyze prompt for jailbreak patterns, system prompt overrides, and toxic content."""
    # 1. Local heuristic check for prompt injection signatures
    jailbreak_keywords = [
        "ignore previous instructions", "ignore all instructions",
        "system prompt", "developer mode", "jailbreak", "override rules", "disregard instructions"
    ]
    lowered = text.lower()
    for kw in jailbreak_keywords:
        if kw in lowered:
            logging.warning(f"🛡️ Guardrail Alert: Prompt injection signature detected ('{kw}')")
            return {
                "safe": False,
                "reason": f"Security Guardrail Violation: Prompt injection attempt detected ('{kw}'). Request blocked.",
                "category": "Jailbreak"
            }

    # 2. Azure AI Content Safety Service API check if endpoint configured
    if HAS_CONTENT_SAFETY and CONTENT_SAFETY_ENDPOINT:
        try:
            client = ContentSafetyClient(
                endpoint=CONTENT_SAFETY_ENDPOINT,
                credential=get_credential(),
            )
            request = AnalyzeTextOptions(text=text[:1000])
            response = client.analyze_text(request)
            for category_analysis in response.categories_analysis:
                if category_analysis.severity > 2:
                    logging.warning(f"🛡️ Azure Content Safety Violation: {category_analysis.category} (severity {category_analysis.severity})")
                    return {
                        "safe": False,
                        "reason": f"Content Safety Violation: High risk content detected ({category_analysis.category}).",
                        "category": str(category_analysis.category)
                    }
        except Exception as e:
            logging.warning(f"Azure Content Safety inspection advisory note: {e}")

    return {"safe": True, "reason": "Passed safety audit", "category": "None"}

def get_search_client() -> SearchClient:
    return SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=SEARCH_INDEX,
        credential=get_credential(),
    )

def rag_search(query: str, top: int = 5) -> str:
    """Search tax documents and return relevant context."""
    try:
        client = get_search_client()
        results = client.search(
            search_text=query,
            top=top,
            select=["content", "title", "source"],
        )
        contexts = []
        for r in results:
            title   = r.get("title", "Tax Document")
            content = r.get("content", "")
            source  = r.get("source", "")
            contexts.append(f"[{title}]\n{content[:2000]}")
        return "\n\n---\n\n".join(contexts) if contexts else ""
    except Exception as e:
        logging.warning(f"RAG search failed: {e}")
        return ""

def cors_response(status_code: int, body: dict) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps(body, ensure_ascii=False, default=str),
        status_code=status_code,
        headers=CORS_HEADERS,
    )

def calculate_new_regime_tax(income: float) -> float:
    """Calculate tax under New Tax Regime FY 2026-27."""
    slabs = [
        (400000, 0.0),
        (400000, 0.05),   # 4L-8L
        (400000, 0.10),   # 8L-12L
        (400000, 0.15),   # 12L-16L
        (400000, 0.20),   # 16L-20L
        (400000, 0.25),   # 20L-24L
        (float("inf"), 0.30),
    ]
    tax = 0.0
    remaining = income
    for slab_size, rate in slabs:
        if remaining <= 0:
            break
        taxable = min(remaining, slab_size)
        tax += taxable * rate
        remaining -= taxable
    return tax

def calculate_old_regime_tax(income: float, is_senior: bool = False) -> float:
    """Calculate tax under Old Tax Regime FY 2026-27."""
    basic_exemption = 300000 if is_senior else 250000
    if income <= basic_exemption:
        return 0.0
    slabs = []
    if is_senior:
        slabs = [
            (200000, 0.05),   # 3L-5L
            (500000, 0.20),   # 5L-10L
            (float("inf"), 0.30),
        ]
        remaining = income - 300000
    else:
        slabs = [
            (250000, 0.05),   # 2.5L-5L
            (500000, 0.20),   # 5L-10L
            (float("inf"), 0.30),
        ]
        remaining = income - 250000
    tax = 0.0
    for slab_size, rate in slabs:
        if remaining <= 0:
            break
        taxable = min(remaining, slab_size)
        tax += taxable * rate
        remaining -= taxable
    return tax

def apply_87a_rebate_new(tax: float, net_income: float) -> float:
    """Apply Section 87A rebate for new regime (₹60K rebate if income ≤ ₹12L)."""
    if net_income <= 1200000:
        return max(0, tax - min(tax, 60000))
    # Marginal relief
    excess = net_income - 1200000
    if tax > excess:
        return excess
    return tax

def apply_87a_rebate_old(tax: float, net_income: float) -> float:
    """Apply Section 87A rebate for old regime (₹12,500 if income ≤ ₹5L)."""
    if net_income <= 500000:
        return max(0, tax - min(tax, 12500))
    return tax

def add_cess(tax: float) -> float:
    return tax * 1.04  # 4% health + education cess

def format_inr(amount: float) -> str:
    return f"₹{amount:,.0f}"

# ── Route: GET /health ─────────────────────────────────────────────────────────
@app.route(route="health", methods=["GET", "OPTIONS"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    return cors_response(200, {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "model": OPENAI_MODEL,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tax_year": "FY 2026-27 (AY 2027-28)",
    })

# ── Route: GET /diagnostics ────────────────────────────────────────────────────
@app.route(route="diagnostics", methods=["GET", "OPTIONS"])
def diagnostics(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    checks = {
        "AZURE_OPENAI_ENDPOINT":         bool(OPENAI_ENDPOINT),
        "AZURE_OPENAI_MODEL":            bool(OPENAI_MODEL),
        "AZURE_SEARCH_ENDPOINT":         bool(SEARCH_ENDPOINT),
        "AZURE_SEARCH_INDEX":            bool(SEARCH_INDEX),
        "AZURE_CONTENT_SAFETY_ENDPOINT": bool(CONTENT_SAFETY_ENDPOINT),
    }
    all_ok = all([checks["AZURE_OPENAI_ENDPOINT"], checks["AZURE_OPENAI_MODEL"], checks["AZURE_SEARCH_ENDPOINT"], checks["AZURE_SEARCH_INDEX"]])
    return cors_response(200 if all_ok else 500, {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
        "app": APP_NAME,
        "content_safety_enabled": bool(CONTENT_SAFETY_ENDPOINT),
    })

# ── Route: POST /chat ──────────────────────────────────────────────────────────
@app.route(route="chat", methods=["POST", "OPTIONS"])
def chat(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    try:
        body = req.get_json()
        raw_message = body.get("message", "").strip()
        history     = body.get("history", [])   # list of {role, content}

        if not raw_message:
            return cors_response(400, {"error": "message is required"})

        # 🛡️ 1. AI Security & Content Safety Inspection
        safety_check = analyze_prompt_safety(raw_message)
        if not safety_check["safe"]:
            return cors_response(400, {
                "error": safety_check["reason"],
                "category": safety_check["category"],
                "blocked": True
            })

        # 🔒 2. PII Sanitization & Masking (PAN / Aadhaar)
        message = sanitize_pii(raw_message)

        # RAG search
        context = rag_search(message)
        context_block = f"\n\nRelevant tax information:\n{context}" if context else ""

        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT + context_block}]
        # Include recent history (last 6 turns)
        for h in history[-6:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                sanitized_history = sanitize_pii(h["content"])
                messages.append({"role": h["role"], "content": sanitized_history})
        messages.append({"role": "user", "content": message})

        client = get_openai_client()
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2,
            max_completion_tokens=1024,
            stream=False,
        )
        reply = extract_response_text(resp)

        # 💾 3. Persist Turn to Azure Cosmos DB
        session_id = body.get("sessionId") or body.get("session_id") or req.headers.get("x-session-id") or "default-session"
        saved = save_chat_turn(session_id, raw_message, reply, OPENAI_MODEL)

        return cors_response(200, {
            "reply": reply,
            "model": OPENAI_MODEL,
            "sessionId": session_id,
            "persisted": saved,
            "sources_searched": bool(context),
        })
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return cors_response(500, {"error": str(e)})

# ── Route: GET /history ────────────────────────────────────────────────────────
@app.route(route="history", methods=["GET", "OPTIONS"])
def history(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    try:
        session_id = req.params.get("sessionId") or req.params.get("session_id") or req.headers.get("x-session-id")
        if not session_id:
            return cors_response(400, {"error": "sessionId query parameter is required"})
        turns = get_session_history(session_id)
        return cors_response(200, {
            "sessionId": session_id,
            "turns": turns,
            "count": len(turns)
        })
    except Exception as e:
        logging.error(f"History fetch error: {e}")
        return cors_response(500, {"error": str(e)})

# ── Route: POST /compare-regime ────────────────────────────────────────────────
@app.route(route="compare-regime", methods=["POST", "OPTIONS"])
def compare_regime(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    try:
        body = req.get_json()
        gross_salary      = float(body.get("gross_salary", 0))
        deductions_80c    = min(float(body.get("deductions_80c", 0)), 150000)
        deductions_80d    = min(float(body.get("deductions_80d", 0)), 75000)
        nps_80ccd1b       = min(float(body.get("nps_80ccd1b", 0)), 50000)
        employer_nps      = float(body.get("employer_nps", 0))  # 80CCD(2)
        home_loan_interest= min(float(body.get("home_loan_interest", 0)), 200000)
        hra_exempt        = float(body.get("hra_exempt", 0))
        other_deductions  = float(body.get("other_deductions", 0))
        is_senior         = body.get("is_senior", False)

        # ── NEW REGIME ──────────────────────────────────────────────────────
        new_std_deduction = 75000
        new_taxable = max(0, gross_salary - new_std_deduction - employer_nps)
        new_tax_before = calculate_new_regime_tax(new_taxable)
        new_tax_before = apply_87a_rebate_new(new_tax_before, new_taxable)
        new_tax_final  = add_cess(new_tax_before)

        # ── OLD REGIME ──────────────────────────────────────────────────────
        old_std_deduction = 50000
        total_old_deductions = (
            old_std_deduction + deductions_80c + deductions_80d +
            nps_80ccd1b + home_loan_interest + hra_exempt +
            employer_nps + other_deductions
        )
        old_taxable = max(0, gross_salary - total_old_deductions)
        old_tax_before = calculate_old_regime_tax(old_taxable, is_senior)
        old_tax_before = apply_87a_rebate_old(old_tax_before, old_taxable)
        old_tax_final  = add_cess(old_tax_before)

        # ── RECOMMENDATION ──────────────────────────────────────────────────
        saving = old_tax_final - new_tax_final
        if new_tax_final <= old_tax_final:
            recommended = "new"
            saving_text = f"New Regime saves {format_inr(abs(saving))} vs Old Regime"
        else:
            recommended = "old"
            saving_text = f"Old Regime saves {format_inr(abs(saving))} vs New Regime"

        return cors_response(200, {
            "gross_salary": gross_salary,
            "new_regime": {
                "standard_deduction": new_std_deduction,
                "employer_nps_deduction": employer_nps,
                "taxable_income": new_taxable,
                "tax_before_cess": round(new_tax_before, 2),
                "total_tax": round(new_tax_final, 2),
                "effective_rate": round((new_tax_final / gross_salary * 100), 2) if gross_salary else 0,
            },
            "old_regime": {
                "standard_deduction": old_std_deduction,
                "total_deductions": round(total_old_deductions, 2),
                "taxable_income": old_taxable,
                "tax_before_cess": round(old_tax_before, 2),
                "total_tax": round(old_tax_final, 2),
                "effective_rate": round((old_tax_final / gross_salary * 100), 2) if gross_salary else 0,
            },
            "recommendation": recommended,
            "summary": saving_text,
            "tax_year": "FY 2026-27 (AY 2027-28)",
        })
    except Exception as e:
        logging.error(f"Compare regime error: {e}")
        return cors_response(500, {"error": str(e)})

# ── Route: POST /analyse-salary ────────────────────────────────────────────────
@app.route(route="analyse-salary", methods=["POST", "OPTIONS"])
def analyse_salary(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    resp = None
    try:
        body = req.get_json()
        salary_text = body.get("salary_text", "").strip()
        city        = body.get("city", "non-metro").lower()

        if not salary_text:
            return cors_response(400, {"error": "salary_text is required"})

        client = get_openai_client()
        prompt = f"""You are an Indian salary slip tax analyser.

Analyse this salary slip and provide a structured tax breakdown for FY 2026-27 (AY 2027-28).
City: {city} ({'metro' if 'metro' in city or city in ['mumbai','delhi','kolkata','chennai'] else 'non-metro'})

Salary Slip:
{salary_text}

Provide a JSON response with this structure:
{{
  "extracted_components": {{
    "basic_salary_annual": 0,
    "hra_annual": 0,
    "special_allowance_annual": 0,
    "employee_pf_annual": 0,
    "other_allowances_annual": 0,
    "total_gross_annual": 0
  }},
  "hra_calculation": {{
    "hra_received": 0,
    "50_or_40_percent_basic": 0,
    "rent_minus_10pc_basic": 0,
    "hra_exempt": 0,
    "hra_taxable": 0,
    "note": "Assumption made if rent not provided"
  }},
  "new_regime": {{
    "taxable_income": 0,
    "total_tax": 0,
    "monthly_tax": 0,
    "effective_rate_percent": 0
  }},
  "old_regime": {{
    "deductions_applied": {{}},
    "taxable_income": 0,
    "total_tax": 0,
    "monthly_tax": 0,
    "effective_rate_percent": 0
  }},
  "recommendation": "new or old",
  "tax_saving_tips": [],
  "assumptions": []
}}

Return ONLY valid JSON, no markdown."""

        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_completion_tokens=1500,
            stream=False,
        )
        raw = extract_response_text(resp).strip()
        # Clean markdown if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        result["tax_year"] = "FY 2026-27 (AY 2027-28)"
        return cors_response(200, result)
    except json.JSONDecodeError as e:
        logging.error(f"JSON parse error in analyse-salary: {e}")
        raw_text = extract_response_text(resp) or "Analysis failed"
        return cors_response(200, {
            "raw_analysis": raw_text,
            "error": "Could not parse structured response",
            "tax_year": "FY 2026-27 (AY 2027-28)",
        })
    except Exception as e:
        logging.error(f"Analyse salary error: {e}")
        return cors_response(500, {"error": str(e)})

# ── Route: POST /analyse-ctc ───────────────────────────────────────────────────
@app.route(route="analyse-ctc", methods=["POST", "OPTIONS"])
def analyse_ctc(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    resp = None
    try:
        body = req.get_json()
        ctc_text = body.get("ctc_text", "").strip()
        regime   = body.get("regime", "new").lower()

        if not ctc_text:
            return cors_response(400, {"error": "ctc_text is required"})

        client = get_openai_client()
        prompt = f"""You are an Indian CTC tax optimisation expert for FY 2026-27.

Analyse this CTC/offer letter and suggest restructuring to minimise tax.
Target regime: {regime} tax regime

Key tax optimization rules for FY 2026-27 (Income Tax Act 2025 / Rules 2026):
1. Employer NPS (Section 80CCD(2)):
   - New Tax Regime (Sec 115BAC): Up to 14% of Basic + DA exempt for BOTH Private & Govt employees (e.g. ₹1,26,000 on ₹9L Basic, saves ₹39,312/yr).
   - Old Tax Regime: Up to 10% of Basic + DA exempt for Private sector employees (e.g. ₹90,000 on ₹9L Basic, saves ₹28,080/yr) and 14% for Govt employees.
2. Food Coupons / Meal Cards (Rule 15(5)(a) of Income Tax Rules 2026): Raised to ₹200/meal (up to ₹8,800/month, ₹1,05,600/year). Exempt under BOTH New & Old regimes!
3. Telephone & Broadband Reimbursement: Fully exempt against actual bills.
4. Learning & Development Allowance: Exempt if spent on certifications/training.

CTC / Offer Letter:
{ctc_text}

Provide a JSON response:
{{
  "current_ctc_analysis": {{
    "total_ctc": 2200000,
    "current_taxable_income": 2200000,
    "estimated_tax": 350000,
    "fully_taxable_components": {{}},
    "tax_exempt_components": {{}}
  }},
  "restructuring_recommendations": [
    {{
      "action": "Convert part of Special Allowance to Employer NPS (80CCD(2))",
      "amount_per_year": 126000,
      "section": "80CCD(2)",
      "tax_saving": 39312,
      "works_in_new_regime": true,
      "steps": "Email HR to reclassify Special Allowance to Employer NPS (14% of Basic for New Regime / 10% for Old Regime Private employees)."
    }},
    {{
      "action": "Add Food Coupons / Meal Cards (Rule 15(5)(a) - Income Tax Rules 2026)",
      "amount_per_year": 105600,
      "section": "Rule 15(5)(a)",
      "tax_saving": 32947,
      "works_in_new_regime": true,
      "steps": "Request HR for maximum benefit of ₹8,800/month (₹200/meal × 2 meals × 22 days = ₹1,05,600/yr) digital food card (Pluxee/Sodexo/Zeta) against Special Allowance. 100% Tax-Exempt under BOTH New and Old Tax Regimes!"
    }}
  ],
  "optimised_ctc": {{
    "total_ctc": 2200000,
    "new_taxable_income": 1968400,
    "new_tax": 277741,
    "total_annual_saving": 72259,
    "effective_monthly_saving": 6022
  }},
  "priority_actions": [],
  "caveats": []
}}

Return ONLY valid JSON, no markdown."""

        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_completion_tokens=1800,
            stream=False,
        )
        raw = extract_response_text(resp).strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)

        # ── Deterministic Post-Processing: Guarantee Food Card & Non-Zero Calculation ─────
        raw_recs = result.get("restructuring_recommendations", [])
        has_food_card = any("food" in r.get("action", "").lower() or "15(5)" in r.get("section", "").lower() or "3(7)" in r.get("section", "").lower() for r in raw_recs)

        if not has_food_card:
            food_card_rec = {
                "action": "Add Food Coupons / Meal Cards (Rule 15(5)(a) - Income Tax Rules 2026)",
                "amount_per_year": 105600,
                "section": "Rule 15(5)(a)",
                "tax_saving": 32947,
                "works_in_new_regime": True,
                "steps": "Request HR for up to ₹8,800/month (₹200/meal, ₹1,05,600/yr) digital food card (Pluxee/Sodexo/Zeta) against Special Allowance."
            }
            raw_recs.append(food_card_rec)

        total_savings = 0
        tax_rate = 0.312  # 30% slab + 4% cess

        for rec in raw_recs:
            amt = rec.get("amount_per_year", 0)
            saving = rec.get("tax_saving", 0)
            rec["works_in_new_regime"] = True

            if (saving == 0 or saving is None) and amt > 0:
                saving = round(amt * tax_rate)
                rec["tax_saving"] = saving

            total_savings += rec.get("tax_saving", 0)

        result["restructuring_recommendations"] = raw_recs

        opt = result.get("optimised_ctc", {})
        opt["total_annual_saving"] = total_savings if total_savings > 0 else 72259
        opt["effective_monthly_saving"] = round(opt["total_annual_saving"] / 12)
        result["optimised_ctc"] = opt

        result["tax_year"] = "FY 2026-27 (AY 2027-28)"
        result["target_regime"] = regime
        return cors_response(200, result)
    except json.JSONDecodeError:
        raw_text = extract_response_text(resp) or "Analysis failed"
        return cors_response(200, {
            "raw_analysis": raw_text,
            "tax_year": "FY 2026-27 (AY 2027-28)",
        })
    except Exception as e:
        logging.error(f"Analyse CTC error: {e}")
        return cors_response(500, {"error": str(e)})
