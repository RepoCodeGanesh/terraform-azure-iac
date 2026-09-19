"""
BankCompliance AI — LangGraph StateGraph Multi-Agent Orchestrator (v2)
========================================================================
Skill Bridge Phase 2 (A1): Production-grade cyclic multi-agent StateGraph
coordinating Supervisor / Planner, Retriever, Auditor (reflection loop),
and Synthesizer with full Langfuse tracing and G2 token circuit breaker.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.core.telemetry import trace_agent_span
from app.services.agents.agent_state import AgentExecutionState
from app.services.agents.supervisor_agent import SupervisorAgent
from app.services.agents.retriever_agent import RetrieverAgent
from app.services.agents.auditor_agent import AuditorAgent
from app.services.agents.orchestrator import (
    MultiAgentOrchestrator,
    _check_and_increment_token_budget,
    SYSTEM_PROMPT,
    GREETING_RESPONSE
)
from app.services.citation_validator import (
    should_abstain_query,
    ABSTAIN_RESPONSE_TEMPLATE,
    OUT_OF_SCOPE_RESPONSE_TEMPLATE
)

logger = logging.getLogger(__name__)

# Attempt to import LangGraph; if missing, graceful fallback is enabled
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    StateGraph = None
    END = None
    LANGGRAPH_AVAILABLE = False
    logger.warning("langgraph package not found; LangGraphOrchestrator will fallback to MultiAgentOrchestrator")


# ── LangGraph Node Functions ──────────────────────────────────────────────────

async def supervisor_node(state: AgentExecutionState) -> AgentExecutionState:
    """Supervisor/Planner Node: Analyzes query intent, domains, and decomposes sub-tasks."""
    with trace_agent_span("langgraph_supervisor_plan", "SupervisorAgent", "gemini-2.0-flash-lite") as span:
        state = await SupervisorAgent.plan(state)
        span.set_attribute("gen_ai.intent", state.get("intent", "compliance_query"))
        span.set_attribute("langgraph.node", "supervisor")
    return state


async def retriever_node(state: AgentExecutionState) -> AgentExecutionState:
    """Retriever Node: Vector similarity search across RBI Master Directions via Qdrant."""
    iter_idx = state.get("iteration_count", 0) + 1
    with trace_agent_span(f"langgraph_retriever_iter_{iter_idx}", "RetrieverAgent") as span:
        state = await RetrieverAgent.retrieve(state)
        span.set_attribute("gen_ai.retrieved_count", len(state.get("retrieved_evidence", [])))
        span.set_attribute("langgraph.node", "retriever")
    return state


async def auditor_node(state: AgentExecutionState) -> AgentExecutionState:
    """Auditor Node: Statutory reflection, citation cross-examination, and halluncination check."""
    iter_idx = state.get("iteration_count", 0) + 1
    with trace_agent_span(f"langgraph_auditor_iter_{iter_idx}", "AuditorAgent", "gemini-2.0-flash-thinking") as span:
        state = await AuditorAgent.audit(state)
        state["iteration_count"] = iter_idx
        span.set_attribute("gen_ai.audit_passed", state.get("audit_passed", True))
        span.set_attribute("langgraph.node", "auditor")
    return state


async def greeting_node(state: AgentExecutionState) -> AgentExecutionState:
    """Fast-Path Greeting Node: Immediate conversational welcome without vector overhead."""
    state["final_answer"] = GREETING_RESPONSE
    state["citations"] = []
    state["model_used"] = "conversational-intent-router"
    return state


async def out_of_scope_node(state: AgentExecutionState) -> AgentExecutionState:
    """Governance Shield Node: Intercepts queries outside Indian Banking Regulatory Scope."""
    state["final_answer"] = OUT_OF_SCOPE_RESPONSE_TEMPLATE
    state["citations"] = []
    state["model_used"] = "governance-abstention-shield"
    return state


async def synthesizer_node(state: AgentExecutionState) -> AgentExecutionState:
    """Synthesizer Node: Multi-model generation with LiteLLM and regulatory context."""
    sanitized_query = state.get("sanitized_query", "")
    retrieved = state.get("retrieved_evidence", [])

    if should_abstain_query(sanitized_query, retrieved):
        state["final_answer"] = ABSTAIN_RESPONSE_TEMPLATE
        state["model_used"] = "deterministic-policy"
        return state

    context_str = "\n\n---\n\n".join([
        f"**Circular:** {c.get('circular_no')}\n**Title:** {c.get('title')}\n**Clause:** {c.get('clause')}\n**Text:** {c.get('text')}"
        for c in state.get("citations", [])
    ])

    user_content = f"Regulatory Context:\n{context_str}\n\nCompliance Query:\n{state['sanitized_query']}"

    with trace_agent_span("langgraph_synthesizer", "SynthesizerAgent", "gemini-2.0-flash") as span:
        answer, model_used = await MultiAgentOrchestrator._call_llm_with_fallback(user_content, state.get("citations", []))
        span.set_attribute("gen_ai.final_model_selected", model_used)
        span.set_attribute("langgraph.node", "synthesizer")

    state["final_answer"] = answer
    state["model_used"] = f"{model_used}:langgraph-v2"
    return state


# ── Conditional Routing Functions ─────────────────────────────────────────────

def route_intent(state: AgentExecutionState) -> str:
    """Routes execution after Supervisor analysis."""
    intent = state.get("intent", "compliance_query")
    if intent == "greeting":
        return "greeting"
    elif intent == "out_of_scope":
        return "out_of_scope"
    return "retriever"


def route_audit_verdict(state: AgentExecutionState) -> str:
    """Reflection conditional edge: loops back to retriever if audit fails (max 2 iterations)."""
    passed = state.get("audit_passed", True)
    iterations = state.get("iteration_count", 0)

    if passed or iterations >= 2:
        return "synthesize"
    logger.info("LangGraph Auditor: Audit failed; triggering reflection loop back to retriever (iter %d)", iterations)
    return "retry_retrieve"


# ── Graph Compilation ─────────────────────────────────────────────────────────

_compiled_graph = None

def _get_or_compile_graph():
    global _compiled_graph
    if _compiled_graph is not None:
        return _compiled_graph

    if not LANGGRAPH_AVAILABLE:
        return None

    graph_builder = StateGraph(AgentExecutionState)

    # 1. Add all micro-agent nodes
    graph_builder.add_node("supervisor", supervisor_node)
    graph_builder.add_node("retriever", retriever_node)
    graph_builder.add_node("auditor", auditor_node)
    graph_builder.add_node("synthesizer", synthesizer_node)
    graph_builder.add_node("greeting", greeting_node)
    graph_builder.add_node("out_of_scope", out_of_scope_node)

    # 2. Entry point
    graph_builder.set_entry_point("supervisor")

    # 3. Intent branching
    graph_builder.add_conditional_edges(
        "supervisor",
        route_intent,
        {
            "greeting": "greeting",
            "out_of_scope": "out_of_scope",
            "retriever": "retriever",
        }
    )

    # 4. Terminal fast-paths
    graph_builder.add_edge("greeting", END)
    graph_builder.add_edge("out_of_scope", END)

    # 5. Retrieval ➔ Audit
    graph_builder.add_edge("retriever", "auditor")

    # 6. Reflection loop conditional edge
    graph_builder.add_conditional_edges(
        "auditor",
        route_audit_verdict,
        {
            "synthesize": "synthesizer",
            "retry_retrieve": "retriever",
        }
    )

    # 7. Synthesizer ➔ End
    graph_builder.add_edge("synthesizer", END)

    _compiled_graph = graph_builder.compile()
    logger.info("✅ BankCompliance LangGraph v2 StateGraph successfully compiled.")
    return _compiled_graph


# ── Public LangGraph Orchestrator Interface ───────────────────────────────────

class LangGraphOrchestrator:
    """Production StateGraph Orchestrator implementing LangGraph cyclic reflection workflow."""

    @staticmethod
    async def run(
        sanitized_query: str,
        department: str = "compliance",
        session_id: str = "default-session",
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        # G2 Token Budget Circuit Breaker Pre-Flight Check
        if not _check_and_increment_token_budget(estimated_tokens=2000):
            return {
                "answer": (
                    "⚠️ **Daily AI Token Budget Reached**\n\n"
                    "The BankCompliance AI token budget for today has been exhausted. "
                    "The system will automatically reset at midnight UTC. "
                    "Please try again tomorrow, or contact your platform administrator "
                    "to increase the `DAILY_TOKEN_BUDGET` limit."
                ),
                "citations": [],
                "suggested_queries": [],
                "model_used": "token-budget-circuit-breaker"
            }

        graph = _get_or_compile_graph()
        if graph is None:
            logger.info("LangGraph unavailable or uncompiled — delegating to MultiAgentOrchestrator")
            return await MultiAgentOrchestrator.run(
                sanitized_query=sanitized_query,
                department=department,
                session_id=session_id,
                history=history
            )

        initial_state: AgentExecutionState = {
            "original_query": sanitized_query,
            "sanitized_query": sanitized_query,
            "department": department,
            "session_id": session_id,
            "history": history or [],
            "intent": "compliance_query",
            "sub_tasks": [],
            "identified_domains": [],
            "retrieved_evidence": [],
            "audit_passed": False,
            "audit_feedback": [],
            "iteration_count": 0,
            "final_answer": "",
            "citations": [],
            "suggested_followups": [],
            "model_used": "langgraph-state-machine"
        }

        try:
            final_state = await graph.ainvoke(initial_state)
            return {
                "answer": final_state.get("final_answer", ""),
                "citations": final_state.get("citations", []),
                "suggested_queries": final_state.get("suggested_followups", []),
                "model_used": final_state.get("model_used", "langgraph-v2")
            }
        except Exception as exc:
            logger.error("LangGraph ainvoke error: %s — falling back to standard orchestrator", exc, exc_info=True)
            return await MultiAgentOrchestrator.run(
                sanitized_query=sanitized_query,
                department=department,
                session_id=session_id,
                history=history
            )
