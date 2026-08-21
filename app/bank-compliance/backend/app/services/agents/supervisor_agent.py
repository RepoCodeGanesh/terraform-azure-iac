"""
BankCompliance AI — Supervisor / Planner Agent
==============================================
Role: Fast Decomposition & Intent Planning
Model: Google Gemini 2.0 Flash-Lite (Fast sub-100ms execution)
"""

import re
import logging
from typing import Dict, Any, List
from app.services.agents.agent_state import AgentExecutionState

logger = logging.getLogger(__name__)

# RBI Regulatory Domain Taxonomy
DOMAIN_KEYWORDS = {
    "kyc": ["kyc", "nri", "v-cip", "video kyc", "ovd", "passport", "customer identification", "aadhaar", "pan"],
    "it_governance": ["cloud", "data localization", "cybersecurity", "meity", "disaster recovery", "dr site", "data residue", "bcp"],
    "outsourcing": ["outsourcing", "vendor", "fintech", "ciso", "sub-contracting", "core management", "soc-2", "third-party"],
    "digital_payments": ["tokenisation", "tokenization", "card", "coft", "cvv", "payment", "tsp", "merchant", "checkout"]
}

class SupervisorAgent:
    """Planner Agent: Breaks down regulatory inquiries into isolated search tasks."""
    
    @staticmethod
    def plan(state: AgentExecutionState) -> AgentExecutionState:
        query = state["sanitized_query"].lower()
        sub_tasks: List[str] = []
        identified_domains: List[str] = []
        
        # 1. Identify applicable compliance domains
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", query) for kw in keywords):
                identified_domains.append(domain)
                
        # 2. Decompose query into sub-tasks based on detected regulatory domains
        if len(identified_domains) > 1:
            for domain in identified_domains:
                clean_name = domain.replace('_', ' ').title()
                sub_tasks.append(f"RBI {clean_name} requirements for: {state['sanitized_query']}")
        else:
            # Single domain or general inquiry
            sub_tasks.append(state["sanitized_query"])
            if not identified_domains:
                identified_domains.append("general_compliance")
                
        state["sub_tasks"] = sub_tasks
        state["identified_domains"] = identified_domains
        logger.info("SupervisorAgent planned %d sub-tasks across domains: %s", len(sub_tasks), identified_domains)
        return state
