"""
BankCompliance AI — Legal & Hallucination Auditor Agent
======================================================
Role: Reflection, Citation Verification & Self-Correction Critic
Model: Google Gemini 2.0 Flash-Thinking via LiteLLM
"""

import json
import logging
from typing import Dict, Any, List
from app.services.agents.agent_state import AgentExecutionState
from app.services.citation_validator import (
    validate_citations_deterministically,
    should_abstain_query
)
from app.services.qdrant_service import LOADED_CLAUSES, load_documents_corpus
from app.core.config import settings

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

AUDITOR_SYSTEM_PROMPT = """You are the Legal & Hallucination Auditor Agent for Indian Banking Compliance.
Evaluate if the retrieved RBI Master Direction citations sufficiently answer the compliance query without legal hallucination.
Output ONLY a JSON object:
{
  "audit_passed": true/false,
  "confidence_score": 0.0 - 1.0,
  "feedback": "brief reason or required search terms"
}
"""

class AuditorAgent:
    """Auditor Agent: Validates legal citations & triggers self-correction loops via Gemini 2.0 Flash-Thinking."""
    
    @staticmethod
    async def audit(state: AgentExecutionState) -> AgentExecutionState:
        evidence = state.get("retrieved_evidence", [])
        corpus = LOADED_CLAUSES or load_documents_corpus()
        
        # 1. Deterministic citation validation against Ground Truth Corpus
        validated_citations, is_valid = validate_citations_deterministically(evidence, corpus)
        
        # 2. Check if the query is an abstain/out-of-scope query
        if should_abstain_query(state["sanitized_query"], evidence):
            state["audit_passed"] = True
            state["citations"] = validated_citations
            return state
            
        # 3. LLM-Assisted Chain-of-Thought Audit via gemini-2.0-flash-thinking
        if httpx and evidence:
            try:
                litellm_url = getattr(settings, "LITELLM_URL", "http://litellm:4000/v1")
                api_key = getattr(settings, "LITELLM_API_KEY", "sk-litellm-proxy-key")
                
                context_summary = "\n".join([f"- {c.get('circular_no')}: {c.get('clause')}" for c in validated_citations[:3]])
                user_prompt = f"Query: {state['sanitized_query']}\nRetrieved Citations:\n{context_summary}"
                
                payload = {
                    "model": "gemini-2.0-flash-thinking",
                    "messages": [
                        {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 150,
                    "temperature": 0.0
                }
                async with httpx.AsyncClient(timeout=4.0) as client:
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
                            if not parsed.get("audit_passed", True) and state.get("iteration_count", 0) < 2:
                                state["audit_passed"] = False
                                state["audit_feedback"] = [parsed.get("feedback", "Additional RBI Master Direction evidence required")]
                                state["iteration_count"] = state.get("iteration_count", 0) + 1
                                logger.warning("AuditorAgent (Thinking model) rejected evidence. Triggering reflection iteration #%d", state["iteration_count"])
                                return state
            except Exception as e:
                logger.debug("AuditorAgent thinking model audit skipped/fallback: %s", e)

        # 4. Standard Reflection logic
        if not evidence or len(validated_citations) == 0:
            if state.get("iteration_count", 0) < 2:
                state["audit_passed"] = False
                state["audit_feedback"] = [
                    f"RBI Master Direction on {d.replace('_', ' ')}"
                    for d in state.get("identified_domains", [])
                ]
                state["iteration_count"] = state.get("iteration_count", 0) + 1
                logger.warning("AuditorAgent rejected evidence. Triggering reflection iteration #%d", state["iteration_count"])
                return state
                
        state["audit_passed"] = True
        state["citations"] = validated_citations
        return state
