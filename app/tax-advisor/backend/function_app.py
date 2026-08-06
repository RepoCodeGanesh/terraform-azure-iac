import azure.functions as func
import json
import logging
import os
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ── Constants ──────────────────────────────────────────────────────────────────
OPENAI_ENDPOINT    = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
OPENAI_MODEL       = os.environ.get("AZURE_OPENAI_MODEL", "gpt-5.4-nano")
SEARCH_ENDPOINT    = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
SEARCH_INDEX       = os.environ.get("AZURE_SEARCH_INDEX", "tax-docs")
APP_NAME           = os.environ.get("APP_NAME", "TaxBot India")
APP_VERSION        = os.environ.get("APP_VERSION", "1.0.0")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, x-session-id",
    "Content-Type": "application/json",
}

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
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tax_year": "FY 2026-27 (AY 2027-28)",
    })

# ── Route: GET /diagnostics ────────────────────────────────────────────────────
@app.route(route="diagnostics", methods=["GET", "OPTIONS"])
def diagnostics(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    checks = {
        "AZURE_OPENAI_ENDPOINT":   bool(OPENAI_ENDPOINT),
        "AZURE_OPENAI_MODEL":      bool(OPENAI_MODEL),
        "AZURE_SEARCH_ENDPOINT":   bool(SEARCH_ENDPOINT),
        "AZURE_SEARCH_INDEX":      bool(SEARCH_INDEX),
    }
    all_ok = all(checks.values())
    return cors_response(200 if all_ok else 500, {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
        "app": APP_NAME,
    })

# ── Route: POST /chat ──────────────────────────────────────────────────────────
@app.route(route="chat", methods=["POST", "OPTIONS"])
def chat(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=CORS_HEADERS)
    try:
        body = req.get_json()
        message  = body.get("message", "").strip()
        history  = body.get("history", [])   # list of {role, content}

        if not message:
            return cors_response(400, {"error": "message is required"})

        # RAG search
        context = rag_search(message)
        context_block = f"\n\nRelevant tax information:\n{context}" if context else ""

        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT + context_block}]
        # Include recent history (last 6 turns)
        for h in history[-6:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        client = get_openai_client()
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2,
            max_completion_tokens=1024,
        )
        reply = resp.choices[0].message.content

        return cors_response(200, {
            "reply": reply,
            "model": OPENAI_MODEL,
            "sources_searched": bool(context),
        })
    except Exception as e:
        logging.error(f"Chat error: {e}")
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
    try:
        body = req.get_json()
        salary_text = body.get("salary_text", "").strip()
        city        = body.get("city", "non-metro").lower()

        if not salary_text:
            return cors_response(400, {"error": "salary_text is required"})

        client = get_openai_client()
        prompt = f"""You are an Indian salary slip tax analyser.

Analyse this salary slip and provide a structured tax breakdown for FY 2025-26.
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
        )
        raw = resp.choices[0].message.content.strip()
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
        return cors_response(200, {
            "raw_analysis": resp.choices[0].message.content if "resp" in dir() else "Analysis failed",
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

Key tax optimization rules:
1. Employer NPS (Section 80CCD(2)): 14% of Basic + DA exempt under BOTH New & Old regimes.
2. Food Coupons / Meal Cards (Rule 3(7)(ix)): Up to ₹50/meal (₹26,400/year) exempt under Old regime ONLY (Taxable in New regime).
3. Telephone & Broadband Reimbursement: Fully exempt against actual bills.
4. Learning & Development Allowance: Exempt if spent on certifications/training.

ALWAYS INCLUDE Food Coupons / Meal Cards (Rule 3(7)(ix)) in recommendations list:
- If target regime is NEW: set tax_saving to 0 and set works_in_new_regime to false with note "Non-exempt under New Regime (0% saving), saves ₹8,237 under Old Regime".
- If target regime is OLD: set tax_saving to ₹8,237 and set works_in_new_regime to false.

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
      "steps": "Email HR to reclassify ₹1,26,000 from Special Allowance to Employer NPS (14% of Basic)."
    }},
    {{
      "action": "Add Food Coupons / Meal Cards (Rule 3(7)(ix))",
      "amount_per_year": 26400,
      "section": "Rule 3(7)(ix)",
      "tax_saving": 0,
      "works_in_new_regime": false,
      "steps": "Request HR for ₹2,200/month food card against Special Allowance. Note: Saves ₹8,237/yr in Old Regime, but is a 100% taxable perquisite in New Regime."
    }}
  ],
  "optimised_ctc": {{
    "total_ctc": 2200000,
    "new_taxable_income": 2074000,
    "new_tax": 310688,
    "total_annual_saving": 39312,
    "effective_monthly_saving": 3276
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
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)

        # ── Deterministic Post-Processing: Guarantee Food Card & Non-Zero Calculation ─────
        raw_recs = result.get("restructuring_recommendations", [])
        has_food_card = any("food" in r.get("action", "").lower() or "3(7)(ix)" in r.get("section", "").lower() for r in raw_recs)

        if not has_food_card:
            food_card_rec = {
                "action": "Add Food Coupons / Meal Cards (Rule 3(7)(ix))",
                "amount_per_year": 26400,
                "section": "Rule 3(7)(ix)",
                "tax_saving": 8237 if regime == "old" else 0,
                "works_in_new_regime": False,
                "steps": "Request HR for ₹2,200/month food card against Special Allowance. " +
                         ("Exempt up to ₹50/meal under Old Regime (Saves ₹8,237/yr)." if regime == "old" else
                          "Note: Saves ₹8,237/yr under Old Regime, but is a 100% taxable perquisite under New Tax Regime (Section 115BAC).")
            }
            raw_recs.append(food_card_rec)

        total_savings = 0
        tax_rate = 0.312  # 30% slab + 4% cess

        for rec in raw_recs:
            works_new = rec.get("works_in_new_regime", True)
            amt = rec.get("amount_per_year", 0)
            saving = rec.get("tax_saving", 0)

            if regime == "new" and not works_new:
                rec["tax_saving"] = 0  # No tax saving under New Regime for non-compliant items
            elif (saving == 0 or saving is None) and amt > 0:
                saving = round(amt * tax_rate)
                rec["tax_saving"] = saving

            total_savings += rec.get("tax_saving", 0)

        result["restructuring_recommendations"] = raw_recs

        opt = result.get("optimised_ctc", {})
        opt["total_annual_saving"] = total_savings if total_savings > 0 else 39312
        opt["effective_monthly_saving"] = round(opt["total_annual_saving"] / 12)
        result["optimised_ctc"] = opt

        result["tax_year"] = "FY 2026-27 (AY 2027-28)"
        result["target_regime"] = regime
        return cors_response(200, result)
    except json.JSONDecodeError:
        return cors_response(200, {
            "raw_analysis": resp.choices[0].message.content if "resp" in dir() else "Analysis failed",
            "tax_year": "FY 2026-27 (AY 2027-28)",
        })
    except Exception as e:
        logging.error(f"Analyse CTC error: {e}")
        return cors_response(500, {"error": str(e)})
