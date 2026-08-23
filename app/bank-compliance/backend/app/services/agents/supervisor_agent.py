"""
BankCompliance AI — Supervisor / Planner Agent
==============================================
Role: Fast Semantic Decomposition & Intent Planning
Model: Google Gemini 2.0 Flash-Lite via LiteLLM
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from app.services.agents.agent_state import AgentExecutionState
from app.core.config import settings

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

# Conversational Greetings & Help Triggers
GREETING_PATTERNS = [
    r"^hi\b", r"^hello\b", r"^hey\b", r"^good\s*(morning|afternoon|evening|day)\b",
    r"^who\s+are\s+you", r"^what\s+can\s+you\s+do", r"^help\b", r"^start\b", r"^greetings\b"
]

DOMAIN_KEYWORDS = {
    "kyc": ["kyc", "nri", "v-cip", "video kyc", "ovd", "passport", "customer identification", "aadhaar", "pan", "re-kyc", "pep", "aml", "cft", "ckyc"],
    "it_governance": ["cloud", "data localization", "cybersecurity", "meity", "disaster recovery", "dr site", "data residue", "bcp", "incident", "soc"],
    "outsourcing": ["outsourcing", "vendor", "fintech", "ciso", "sub-contracting", "core management", "soc-2", "third-party", "sas-70"],
    "digital_payments": ["tokenisation", "tokenization", "card", "coft", "cvv", "payment", "tsp", "merchant", "checkout", "pos", "upi", "credit card", "debit card"],
    "digital_lending": ["lending", "loan", "disbursement", "cooling-off", "lps", "dlr", "recovery agent", "fldg", "first loss default guarantee"]
}

# Broad Banking and Financial Keywords
GENERAL_BANKING_KEYWORDS = [
    "bank", "rbi", "reserve bank", "account", "transaction", "circular", "master direction", "compliance",
    "statutory", "audit", "deposit", "interest", "penalty", "mandate", "regulator", "financial", "fraud",
    "customer", "borrower", "lender", "nbfc", "fintech", "license", "authorization", "kyc", "pan", "aadhaar"
]

DOMAIN_SUGGESTIONS = {
    "kyc": [
        "What are acceptable OVDs for NRI account opening?",
        "What are the mandatory V-CIP video recording rules?",
        "What are the Re-KYC periodic updation timelines?"
    ],
    "it_governance": [
        "Can a bank store transaction data in a public overseas cloud?",
        "What is the maximum reporting window for a cybersecurity breach?",
        "What are the disaster recovery (DR) site requirements?"
    ],
    "outsourcing": [
        "What are the RBI restrictions on outsourcing CISO functions?",
        "Can a core banking management function be outsourced to FinTechs?",
        "What are the audit and SOC-2 requirements for IT service providers?"
    ],
    "digital_payments": [
        "Can a merchant store the 16-digit card PAN after transaction checkout?",
        "What is the penalty for issuing an unsolicited credit card?",
        "What are the CoFT tokenisation rules for payment aggregators?"
    ],
    "digital_lending": [
        "Can loan disbursements pass through a FinTech pool account?",
        "What is the mandatory cooling-off period for digital personal loans?",
        "Can a digital lending app access contact lists or biometric data?"
    ],
    "general": [
        "What are the NRI KYC video verification (V-CIP) rules?",
        "Can bank transaction data reside in an overseas public cloud?",
        "What are the RBI restrictions on outsourcing CISO functions?",
        "Can a merchant store card PAN numbers after CoFT tokenization?"
    ]
}

PLANNER_SYSTEM_PROMPT = """You are the Supervisor Planning Agent for an Indian Banking Regulatory Copilot.
Analyze the user's query and output a JSON object:
1. "intent": "greeting" (if hello/help), "out_of_scope" (if query is NOT related to banking/finance/compliance, like cooking/sports/movies), or "compliance_query" (if banking/RBI/finance related).
2. "domains": list of matching RBI domains from ["kyc", "it_governance", "outsourcing", "digital_payments", "digital_lending"] or empty if out of scope.
3. "sub_tasks": list of concise sub-search queries for vector retrieval.
Output ONLY valid JSON.
"""

class SupervisorAgent:
    """Planner Agent: Classifies intent, resolves conversational history, and plans sub-tasks via Gemini 2.0 Flash-Lite."""
    
    @staticmethod
    async def plan(state: AgentExecutionState) -> AgentExecutionState:
        raw_query = state["sanitized_query"].strip()
        query_lower = raw_query.lower()
        
        # ── 1. Fast Check for Greetings & Help ───────────────────────────────
        for pattern in GREETING_PATTERNS:
            if re.search(pattern, query_lower):
                state["intent"] = "greeting"
                state["sub_tasks"] = []
                state["identified_domains"] = ["greeting"]
                state["suggested_followups"] = DOMAIN_SUGGESTIONS["general"]
                return state

        # ── 2. Multi-Turn History Resolution ──────────────────────────────────
        resolved_query = raw_query
        history = state.get("history") or []
        if history and len(raw_query.split()) <= 6:
            last_user_msg = next((m.get("content", "") for m in reversed(history) if m.get("role") == "user"), "")
            if last_user_msg:
                resolved_query = f"{last_user_msg} -> Specifically: {raw_query}"
                state["sanitized_query"] = resolved_query
                query_lower = resolved_query.lower()

        # ── 3. Call Gemini 2.0 Flash-Lite via LiteLLM for Intent Planning ─────
        planned_via_llm = False
        if httpx:
            try:
                litellm_url = getattr(settings, "LITELLM_URL", "http://litellm:4000/v1")
                api_key = getattr(settings, "LITELLM_API_KEY", "sk-litellm-proxy-key")
                payload = {
                    "model": "gemini-2.0-flash-lite",
                    "messages": [
                        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Query: {resolved_query}"}
                    ],
                    "max_tokens": 150,
                    "temperature": 0.0
                }
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.post(
                        f"{litellm_url}/chat/completions",
                        json=payload,
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"].strip()
                        if "{" in content and "}" in content:
                            json_str = content[content.find("{"):content.rfind("}")+1]
                            parsed = json.loads(json_str)
                            state["intent"] = parsed.get("intent", "compliance_query")
                            state["identified_domains"] = parsed.get("domains", [])
                            state["sub_tasks"] = parsed.get("sub_tasks", [resolved_query])
                            planned_via_llm = True
            except Exception as e:
                logger.debug("SupervisorAgent LLM call fell back to local taxonomy: %s", e)

        # ── 4. Deterministic Out-of-Scope & Domain Classification Guardrail ───
        identified_domains: List[str] = []
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", query_lower) for kw in keywords):
                identified_domains.append(domain)
                
        has_general_banking = any(re.search(rf"\b{re.escape(kw)}\b", query_lower) for kw in GENERAL_BANKING_KEYWORDS)
        
        # If query has zero banking/regulatory relevance, immediately reject as out of scope
        if not identified_domains and not has_general_banking:
            state["intent"] = "out_of_scope"
            state["sub_tasks"] = []
            state["identified_domains"] = []
            state["suggested_followups"] = DOMAIN_SUGGESTIONS["general"]
            return state
            
        if not planned_via_llm or state.get("intent") != "compliance_query":
            state["intent"] = "compliance_query"
            sub_tasks: List[str] = []
            if len(identified_domains) > 1:
                for domain in identified_domains:
                    clean_name = domain.replace('_', ' ').title()
                    sub_tasks.append(f"RBI {clean_name} requirements for: {resolved_query}")
            else:
                sub_tasks.append(resolved_query)
                if not identified_domains:
                    identified_domains.append("general")
                    
            state["sub_tasks"] = sub_tasks
            state["identified_domains"] = identified_domains

        # ── 5. Generate Contextual Follow-up Chips ─────────────────────────────
        primary_domain = state["identified_domains"][0] if state.get("identified_domains") else "general"
        state["suggested_followups"] = DOMAIN_SUGGESTIONS.get(primary_domain, DOMAIN_SUGGESTIONS["general"])
        
        return state
