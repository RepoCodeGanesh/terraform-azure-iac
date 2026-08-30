"""
BankCompliance AI — Multi-Agent Orchestrator
=============================================
Manages state graph flow across Planner, Retriever, Auditor, and Synthesizer,
with primary routing to Azure OpenAI gpt-5.4-nano / Google Gemini 2.0.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.telemetry import trace_agent_span
from app.services.agents.agent_state import AgentExecutionState
from app.services.agents.supervisor_agent import SupervisorAgent
from app.services.agents.retriever_agent import RetrieverAgent
from app.services.agents.auditor_agent import AuditorAgent
from app.services.citation_validator import (
    should_abstain_query,
    ABSTAIN_RESPONSE_TEMPLATE,
    OUT_OF_SCOPE_RESPONSE_TEMPLATE
)

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are BankCompliance AI, the official Banking Regulatory & Compliance Copilot for Indian Scheduled Commercial Banks and NBFCs.
You provide precise, legally auditable interpretations of Reserve Bank of India (RBI) Master Directions, KYC norms, IT Governance, Digital Lending, and Digital Payment regulations.

Rules:
1. Always quote the exact RBI Circular number, Master Direction title, and Section/Clause (e.g. "Under Section 4.2(a) of the RBI Master Direction on KYC...").
2. State clear actionable compliance steps and mandatory statutory penalties for non-compliance.
3. If a user asks for an exemption, waiver, or bypass that contradicts RBI Master Directions, firmly and explicitly clarify that such actions are prohibited under statutory regulations, citing the relevant clauses.
4. Conclude with an audit-proof recommendation for Bank Internal Audit & Chief Compliance Officer (CCO) review.
5. If the user query is unrelated to banking, finance, or RBI regulations (e.g. general chit-chat, cooking, aviation, entertainment), politely refuse by stating you only answer Indian Banking Regulatory & Compliance queries.
"""

GREETING_RESPONSE = """### Welcome to BankCompliance AI 👋

I am your **Reserve Bank of India (RBI) Regulatory & Compliance Copilot** for Scheduled Commercial Banks and NBFCs.

I provide legally auditable, citation-backed interpretations across:
* 📄 **KYC & Customer Onboarding** — Officially Valid Documents (OVDs), Video KYC (V-CIP), CKYCR Registry
* ☁️ **IT Governance & Cybersecurity** — Data Localization, MeitY Cloud Policy, 6-Hour Incident Reporting
* 🤝 **IT Outsourcing & Vendor Risk** — CISO Non-Outsourcing mandates, Core Banking FinTech restrictions
* 💳 **Payment Tokenization & Cards** — CoFT Tokenization, Card-on-File storage bans, Unsolicited card penalties
* 📱 **Digital Lending Guidelines** — First Loss Default Guarantees (FLDG), Cooling-off periods, DLAs

Ask a specific regulatory question below or select from the suggested compliance topics!
"""

class MultiAgentOrchestrator:
    """State Graph Runner coordinating all micro-agents."""

    @staticmethod
    async def run(
        sanitized_query: str,
        department: str = "compliance",
        session_id: str = "default-session",
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        
        # Initialize Agent Execution State
        state: AgentExecutionState = {
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
            "model_used": "gpt-5.4-nano"
        }

        # ── Step 1: Supervisor / Planner Agent (Gemini 2.0 Flash-Lite) ────────
        with trace_agent_span("intent_decomposition", "SupervisorAgent", "gemini-2.0-flash-lite") as span:
            state = await SupervisorAgent.plan(state)
            span.set_attribute("gen_ai.intent", state.get("intent", "compliance_query"))

        # ── Fast Path: Conversational Greeting Intent ──────────────────────────
        if state.get("intent") == "greeting":
            return {
                "answer": GREETING_RESPONSE,
                "citations": [],
                "suggested_queries": state.get("suggested_followups", []),
                "model_used": "conversational-intent-router"
            }

        # ── Fast Path: Out of Scope Intent ─────────────────────────────────────
        if state.get("intent") == "out_of_scope":
            return {
                "answer": OUT_OF_SCOPE_RESPONSE_TEMPLATE,
                "citations": [],
                "suggested_queries": state.get("suggested_followups", []),
                "model_used": "governance-abstention-shield"
            }

        # ── Step 2 & 3: Parallel Tool Retrieval & Auditor Reflection Loop ───────
        for iter_num in range(2):
            with trace_agent_span(f"qdrant_vector_retrieval_iter_{iter_num+1}", "RetrieverAgent") as r_span:
                state = await RetrieverAgent.retrieve(state)
                r_span.set_attribute("gen_ai.retrieved_count", len(state.get("retrieved_evidence", [])))

            with trace_agent_span(f"statutory_reflection_iter_{iter_num+1}", "AuditorAgent", "gemini-2.0-flash-thinking") as a_span:
                state = await AuditorAgent.audit(state)
                a_span.set_attribute("gen_ai.audit_passed", state.get("audit_passed", True))

            if state.get("audit_passed", True):
                break

        # ── Step 4: Governance Abstention & Out-of-Scope Shield ─────────────────
        if should_abstain_query(sanitized_query, state.get("retrieved_evidence", [])):
            return {
                "answer": ABSTAIN_RESPONSE_TEMPLATE,
                "citations": state.get("citations", []),
                "suggested_queries": state.get("suggested_followups", []),
                "model_used": "deterministic-policy"
            }

        # ── Step 5: Synthesizer Agent with LiteLLM & Multi-Model Fallback ──────
        context_str = "\n\n---\n\n".join([
            f"**Circular:** {c.get('circular_no')}\n**Title:** {c.get('title')}\n**Clause:** {c.get('clause')}\n**Text:** {c.get('text')}"
            for c in state.get("citations", [])
        ])

        user_content = f"Regulatory Context:\n{context_str}\n\nCompliance Query:\n{state['sanitized_query']}"
        
        with trace_agent_span("synthesizer_generation", "SynthesizerAgent", "gemini-2.0-flash") as s_span:
            answer, model_used = await MultiAgentOrchestrator._call_llm_with_fallback(user_content, state.get("citations", []))
            s_span.set_attribute("gen_ai.final_model_selected", model_used)
        
        return {
            "answer": answer,
            "citations": state.get("citations", []),
            "suggested_queries": state.get("suggested_followups", []),
            "model_used": model_used
        }

    @staticmethod
    async def _call_llm_with_fallback(user_content: str, citations: List[Dict[str, Any]] = None) -> tuple[str, str]:
        """Calls LiteLLM with Google Gemini 2.0 Flash / Groq as Primary ($0 cost) and Azure OpenAI as DR Fallback."""
        primary_model = getattr(settings, "OPENAI_MODEL", "gemini-2.0-flash") or "gemini-2.0-flash"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        if httpx:
            litellm_url = getattr(settings, "LITELLM_URL", "http://litellm:4000/v1")
            api_key = getattr(settings, "LITELLM_API_KEY", "sk-litellm-proxy-key")

            # ── Multi-Cloud Priority: Primary (Gemini/Groq $0) ➔ Standby DR (Azure OpenAI) ──
            candidate_models = []
            for candidate in [primary_model, "gemini-2.0-flash", "groq-llama-70b", "gpt-5.4-nano"]:
                if candidate and candidate not in candidate_models:
                    candidate_models.append(candidate)

            for m in candidate_models:
                try:
                    payload = {
                        "model": m,
                        "messages": messages,
                        "temperature": 0.1,
                        "max_completion_tokens": 1024
                    }
                    async with httpx.AsyncClient(timeout=25.0) as client:
                        resp = await client.post(
                            f"{litellm_url}/chat/completions",
                            json=payload,
                            headers={"Authorization": f"Bearer {api_key}"}
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            answer = data["choices"][0]["message"]["content"]
                            return answer, data.get("model", m)
                        elif resp.status_code == 400:
                            # Retry with max_tokens if max_completion_tokens is unsupported by model
                            payload.pop("max_completion_tokens", None)
                            payload["max_tokens"] = 1024
                            resp_retry = await client.post(
                                f"{litellm_url}/chat/completions",
                                json=payload,
                                headers={"Authorization": f"Bearer {api_key}"}
                            )
                            if resp_retry.status_code == 200:
                                data = resp_retry.json()
                                answer = data["choices"][0]["message"]["content"]
                                return answer, data.get("model", m)
                except Exception as ex:
                    logger.debug("LiteLLM attempt on %s failed: %s", m, ex)

            # Direct Azure OpenAI Fallback if LiteLLM proxy is unavailable
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_key = os.getenv("AZURE_API_KEY") or os.getenv("OPENAI_API_KEY")
            if azure_endpoint and azure_key:
                try:
                    endpoint_clean = azure_endpoint.rstrip("/")
                    azure_url = f"{endpoint_clean}/openai/deployments/gpt-5.4-nano/chat/completions?api-version=2024-06-01"
                    payload = {
                        "messages": messages,
                        "max_completion_tokens": 1024,
                        "temperature": 0.1
                    }
                    async with httpx.AsyncClient(timeout=25.0) as client:
                        resp = await client.post(
                            azure_url,
                            json=payload,
                            headers={"api-key": azure_key, "Content-Type": "application/json"}
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            return data["choices"][0]["message"]["content"], "azure-openai-direct (gpt-5.4-nano)"
                except Exception as direct_ex:
                    logger.warning("Direct Azure OpenAI call failed: %s", direct_ex)

        # High-Fidelity Dynamic Synthesis from Citations if LLM is offline
        return MultiAgentOrchestrator._synthesize_dynamic_fallback(citations or []), "statutory-evidence-synthesis"

    @staticmethod
    def _synthesize_dynamic_fallback(citations: List[Dict[str, Any]]) -> str:
        """Dynamic compliance synthesis directly grounding the retrieved RBI clauses."""
        if not citations:
            return ABSTAIN_RESPONSE_TEMPLATE

        lines = [
            "### Regulatory Compliance Determination (Statutory Grounding)\n",
            "Based on verified **Reserve Bank of India (RBI) Master Directions**:\n"
        ]
        
        for idx, c in enumerate(citations[:3], 1):
            title = c.get("title", "RBI Master Direction")
            circ = c.get("circular_no", "RBI Norms")
            clause = c.get("clause", "Applicable Clause")
            text = c.get("text", "").strip()
            lines.append(f"{idx}. **{title} ({circ}) — {clause}:**")
            lines.append(f"   > {text}\n")

        lines.extend([
            "**Statutory Audit Determination:**",
            "* All operations must strictly follow the mandatory clauses cited above.",
            "* Any unverified exemption, waiver, or deviation without an official RBI Gazette Notification is **legally non-compliant**.",
            "* **Escalation:** Forward this determination to the Chief Compliance Officer (CCO) and Bank Internal Audit for immediate review."
        ])

        return "\n".join(lines)
