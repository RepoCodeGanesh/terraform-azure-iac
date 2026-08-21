"""
BankCompliance AI — Supervisor / Planner Agent
==============================================
Role: Fast Decomposition & Intent Planning
Model: Google Gemini 2.0 Flash-Lite (Fast sub-100ms execution)
"""

import re
import logging
from typing import Dict, Any, List, Optional
from app.services.agents.agent_state import AgentExecutionState

logger = logging.getLogger(__name__)

# Conversational Greetings & Help Triggers
GREETING_PATTERNS = [
    r"^hi\b", r"^hello\b", r"^hey\b", r"^good\s*(morning|afternoon|evening|day)\b",
    r"^who\s+are\s+you", r"^what\s+can\s+you\s+do", r"^help\b", r"^start\b", r"^greetings\b"
]

# RBI Regulatory Domain Taxonomy
DOMAIN_KEYWORDS = {
    "kyc": ["kyc", "nri", "v-cip", "video kyc", "ovd", "passport", "customer identification", "aadhaar", "pan"],
    "it_governance": ["cloud", "data localization", "cybersecurity", "meity", "disaster recovery", "dr site", "data residue", "bcp"],
    "outsourcing": ["outsourcing", "vendor", "fintech", "ciso", "sub-contracting", "core management", "soc-2", "third-party"],
    "digital_payments": ["tokenisation", "tokenization", "card", "coft", "cvv", "payment", "tsp", "merchant", "checkout"],
    "digital_lending": ["lending", "loan", "disbursement", "cooling-off", "lps", "dlr", "recovery agent"]
}

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

class SupervisorAgent:
    """Planner Agent: Classifies intent, resolves conversational history, and plans sub-tasks."""
    
    @staticmethod
    def plan(state: AgentExecutionState) -> AgentExecutionState:
        raw_query = state["sanitized_query"].strip()
        query_lower = raw_query.lower()
        
        # ── 1. Intent Classification: Check for Greetings & Help ─────────────
        for pattern in GREETING_PATTERNS:
            if re.search(pattern, query_lower):
                state["intent"] = "greeting"
                state["sub_tasks"] = []
                state["identified_domains"] = ["greeting"]
                state["suggested_followups"] = DOMAIN_SUGGESTIONS["general"]
                logger.info("SupervisorAgent classified intent as GREETING.")
                return state
                
        state["intent"] = "compliance_query"

        # ── 2. Multi-Turn History Resolution ──────────────────────────────────
        # If user asks a brief follow-up ("What about for NRIs?", "And penalties?"),
        # combine it with the previous context to ensure accurate retrieval.
        resolved_query = raw_query
        history = state.get("history") or []
        if history and len(raw_query.split()) <= 6:
            # Grab last user message from history
            last_user_msg = next((m.get("content", "") for m in reversed(history) if m.get("role") == "user"), "")
            if last_user_msg:
                resolved_query = f"{last_user_msg} -> Specifically: {raw_query}"
                logger.info("SupervisorAgent resolved follow-up query: '%s' -> '%s'", raw_query, resolved_query)
                state["sanitized_query"] = resolved_query
                query_lower = resolved_query.lower()

        # ── 3. Domain Taxonomy Mapping ────────────────────────────────────────
        sub_tasks: List[str] = []
        identified_domains: List[str] = []
        
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", query_lower) for kw in keywords):
                identified_domains.append(domain)
                
        # ── 4. Decompose Query into Sub-Tasks ─────────────────────────────────
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
        primary_domain = identified_domains[0] if identified_domains else "general"
        state["suggested_followups"] = DOMAIN_SUGGESTIONS.get(primary_domain, DOMAIN_SUGGESTIONS["general"])
        
        logger.info("SupervisorAgent planned %d sub-tasks across domains: %s", len(sub_tasks), identified_domains)
        return state
