"""
BankCompliance AI — Specialized Regulatory Retriever Agent
==========================================================
Role: Vector Search & Evidence Extraction Tool Caller
Model: text-embedding-004 + Qdrant Vector Store
"""

import logging
from typing import List, Dict, Any
from app.services.agents.agent_state import AgentExecutionState
from app.services.qdrant_service import search_rbi_clauses

logger = logging.getLogger(__name__)

class RetrieverAgent:
    """Specialized Tool-Calling Retriever Agent."""
    
    @staticmethod
    async def retrieve(state: AgentExecutionState) -> AgentExecutionState:
        all_evidence: List[Dict[str, Any]] = []
        seen_clauses = set()
        
        # Execute tool calls across all planned sub-tasks
        for sub_task in state.get("sub_tasks", [state["sanitized_query"]]):
            results = await search_rbi_clauses(sub_task, limit=3)
            for item in results:
                clause_key = (item.get("circular_no"), item.get("clause"))
                if clause_key not in seen_clauses:
                    seen_clauses.add(clause_key)
                    all_evidence.append(item)
                    
        # If feedback from auditor exists, inject specific re-search terms
        if state.get("audit_feedback") and state.get("iteration_count", 0) > 0:
            for feedback_term in state["audit_feedback"]:
                fb_results = await search_rbi_clauses(feedback_term, limit=2)
                for item in fb_results:
                    clause_key = (item.get("circular_no"), item.get("clause"))
                    if clause_key not in seen_clauses:
                        seen_clauses.add(clause_key)
                        all_evidence.append(item)
                        
        # Sort evidence by relevance score
        all_evidence.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        state["retrieved_evidence"] = all_evidence[:5]
        logger.info("RetrieverAgent extracted %d verified evidence clauses.", len(state["retrieved_evidence"]))
        return state
