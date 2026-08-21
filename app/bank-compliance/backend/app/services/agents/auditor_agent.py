"""
BankCompliance AI — Legal & Hallucination Auditor Agent
======================================================
Role: Reflection & Self-Correction Critic
Model: Google Gemini 2.0 Flash-Thinking / Deterministic Verification
"""

import logging
from typing import Dict, Any, List
from app.services.agents.agent_state import AgentExecutionState
from app.services.citation_validator import (
    validate_citations_deterministically,
    should_abstain_query
)
from app.services.qdrant_service import LOADED_CLAUSES, load_documents_corpus

logger = logging.getLogger(__name__)

class AuditorAgent:
    """Auditor Agent: Validates legal citations & triggers self-correction loops."""
    
    @staticmethod
    def audit(state: AgentExecutionState) -> AgentExecutionState:
        evidence = state.get("retrieved_evidence", [])
        corpus = LOADED_CLAUSES or load_documents_corpus()
        
        # 1. Deterministic citation validation against Ground Truth Corpus
        validated_citations, is_valid = validate_citations_deterministically(evidence, corpus)
        
        # 2. Check if the query is an abstain/out-of-scope query
        if should_abstain_query(state["sanitized_query"], evidence):
            state["audit_passed"] = True  # Allow graceful escalation/abstention
            state["citations"] = validated_citations
            return state
            
        # 3. Reflection logic: verify evidence coverage
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
        logger.info("AuditorAgent verified %d citations successfully.", len(validated_citations))
        return state
