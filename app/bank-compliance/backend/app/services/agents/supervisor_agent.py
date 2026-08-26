"""
BankCompliance AI — Supervisor / Planner Agent
==============================================
Role: Enterprise Mathematical & Semantic Intent Planning (Layers 1 & 2)
Model: Google Gemini 2.0 Flash-Lite via LiteLLM + Mathematical Vector Centroid Sieve
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from app.services.agents.agent_state import AgentExecutionState
from app.services.agents.domain_guardrail import DomainCentroidGuardrail
from app.core.config import settings

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

# Fast Greeting & Help Sieve (<1ms)
GREETING_PATTERNS = [
    r"^hi\b", r"^hello\b", r"^hey\b", r"^good\s*(morning|afternoon|evening|day)\b",
    r"^who\s+are\s+you", r"^what\s+can\s+you\s+do", r"^help\b", r"^start\b", r"^greetings\b"
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
1. "intent": "greeting" (if hello/help), "out_of_scope" (if query is NOT related to banking/finance/compliance, like cooking/sports/movies/plumbing/general chat), or "compliance_query" (if banking/RBI/finance related).
2. "domains": list of matching RBI domains from ["kyc", "it_governance", "outsourcing", "digital_payments", "digital_lending"] or empty if out of scope.
3. "sub_tasks": list of concise sub-search queries for vector retrieval.
Output ONLY valid JSON.
"""

DISAMBIGUATION_SYSTEM_PROMPT = """You are the Conversational Query Disambiguator for an Indian Banking Compliance Copilot.
Given the chat history and the latest user turn:
1. Determine if the latest turn is a direct follow-up / clarification to the previous banking topic, OR a new unrelated topic.
2. If it is an unrelated topic (e.g. plumbing, food, sports, general knowledge), mark "is_followup": false and keep the query as-is.
3. If it is a genuine follow-up, rewrite it into a self-contained standalone banking query resolving pronouns.
Output ONLY JSON:
{
  "is_followup": true/false,
  "standalone_query": "rewritten query or original query"
}
"""

class SupervisorAgent:
    """Planner Agent: Classifies intent, mathematically guards domain boundaries, and resolves history."""
    
    @staticmethod
    async def plan(state: AgentExecutionState) -> AgentExecutionState:
        raw_query = state["sanitized_query"].strip()
        query_lower = raw_query.lower()
        history = state.get("history") or []
        
        # ── 1. Fast Check for Greetings & Help (<1ms) ─────────────────────────
        for pattern in GREETING_PATTERNS:
            if re.search(pattern, query_lower):
                state["intent"] = "greeting"
                state["sub_tasks"] = []
                state["identified_domains"] = ["greeting"]
                state["suggested_followups"] = DOMAIN_SUGGESTIONS["general"]
                return state

        # ── 2. Layer 1: Mathematical Vector Centroid Guardrail (<3ms) ─────────
        is_in_domain, centroid_sim, max_clause_sim = DomainCentroidGuardrail.evaluate(raw_query)
        logger.info(
            "Layer 1 Centroid Evaluation: '%s' | In-Domain=%s (CentroidSim=%.4f, MaxClauseSim=%.4f)",
            raw_query, is_in_domain, centroid_sim, max_clause_sim
        )

        # ── 3. Layer 2: Conversational Disambiguation (Multi-Turn) ────────────
        resolved_query = raw_query
        
        if history:
            # Multi-turn conversational session
            disambiguated = False
            if httpx:
                try:
                    litellm_url = getattr(settings, "LITELLM_URL", "http://litellm:4000/v1")
                    api_key = getattr(settings, "LITELLM_API_KEY", "sk-litellm-proxy-key")
                    
                    history_snippet = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in history[-3:]])
                    payload = {
                        "model": "gemini-2.0-flash-lite",
                        "messages": [
                            {"role": "system", "content": DISAMBIGUATION_SYSTEM_PROMPT},
                            {"role": "user", "content": f"Chat History:\n{history_snippet}\n\nLatest Turn:\n{raw_query}"}
                        ],
                        "max_tokens": 100,
                        "temperature": 0.0
                    }
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        resp = await client.post(
                            f"{litellm_url}/chat/completions",
                            json=payload,
                            headers={"Authorization": f"Bearer {api_key}"}
                        )
                        if resp.status_code == 200:
                            content = resp.json()["choices"][0]["message"]["content"].strip()
                            if "{" in content and "}" in content:
                                parsed = json.loads(content[content.find("{"):content.rfind("}")+1])
                                is_followup = parsed.get("is_followup", False)
                                if is_followup:
                                    resolved_query = parsed.get("standalone_query", raw_query)
                                    state["sanitized_query"] = resolved_query
                                    # Re-evaluate resolved query mathematically
                                    is_in_domain, centroid_sim, max_clause_sim = DomainCentroidGuardrail.evaluate(resolved_query)
                                disambiguated = True
                except Exception as e:
                    logger.debug("Disambiguation LLM call skipped: %s", e)

            if not disambiguated and not is_in_domain:
                # If offline/fallback and raw query has zero mathematical domain similarity -> Hard Out-of-Scope
                logger.info("SupervisorAgent intercepted off-topic query in multi-turn chat: '%s'", raw_query)
                state["intent"] = "out_of_scope"
                state["sub_tasks"] = []
                state["identified_domains"] = []
                state["suggested_followups"] = DOMAIN_SUGGESTIONS["general"]
                return state
        else:
            # Standalone single-turn query: If mathematically out of domain, immediately reject
            if not is_in_domain:
                logger.info("SupervisorAgent mathematically intercepted off-topic query in <3ms: '%s'", raw_query)
                state["intent"] = "out_of_scope"
                state["sub_tasks"] = []
                state["identified_domains"] = []
                state["suggested_followups"] = DOMAIN_SUGGESTIONS["general"]
                return state

        # ── 4. Call Gemini 2.0 Flash-Lite via LiteLLM for Intent Planning ─────
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
                async with httpx.AsyncClient(timeout=2.5) as client:
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
                logger.debug("SupervisorAgent LLM call fell back to vector taxonomy: %s", e)

        # Post-validation check using mathematical criterion
        if state.get("intent") == "out_of_scope" or not is_in_domain:
            state["intent"] = "out_of_scope"
            state["sub_tasks"] = []
            state["identified_domains"] = []
            state["suggested_followups"] = DOMAIN_SUGGESTIONS["general"]
            return state

        if not planned_via_llm or state.get("intent") != "compliance_query":
            state["intent"] = "compliance_query"
            state["sub_tasks"] = [resolved_query]
            if not state.get("identified_domains"):
                state["identified_domains"] = ["general"]

        # ── 5. Generate Contextual Follow-up Chips ─────────────────────────────
        primary_domain = state["identified_domains"][0] if state.get("identified_domains") else "general"
        state["suggested_followups"] = DOMAIN_SUGGESTIONS.get(primary_domain, DOMAIN_SUGGESTIONS["general"])
        
        return state
