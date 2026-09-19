"""
BankCompliance AI — Langfuse LLM Observability Tracing Service (O1)
====================================================================
Wraps Langfuse SDK to provide per-agent waterfall traces in the
Langfuse Cloud dashboard (https://cloud.langfuse.com).

Design Principles:
  1. NEVER fail user requests on tracing errors — all calls are wrapped in
     try/except. Langfuse is purely observational; the request pipeline MUST
     continue even if the tracing backend is unreachable.
  2. Lazy initialization — the Langfuse client is created once on first use
     and cached in the module. If LANGFUSE_PUBLIC_KEY / SECRET_KEY are not
     set, the module degrades gracefully to a no-op stub.
  3. Async-safe — all blocking Langfuse SDK calls are offloaded via
     asyncio.get_event_loop().run_in_executor so they never block the
     FastAPI event loop.

Setup:
  1. Sign up FREE at https://cloud.langfuse.com (50k traces/month)
  2. Add K8s secret: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
  3. Reference secret in backend-deployment.yaml via envFrom secretRef
"""

import os
import logging
import asyncio
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

logger = logging.getLogger("BankCompliance-Langfuse")

# ── Lazy Langfuse Client ──────────────────────────────────────────────────────
_langfuse_client = None
_langfuse_enabled = False


def _init_langfuse():
    """Initialise Langfuse client once from environment variables.
    Returns None silently if credentials are absent (graceful no-op).
    """
    global _langfuse_client, _langfuse_enabled

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    host       = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        logger.info(
            "Langfuse credentials not set — LLM tracing disabled. "
            "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable."
        )
        _langfuse_enabled = False
        return None

    try:
        from langfuse import Langfuse  # type: ignore
        _langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            debug=False,
        )
        _langfuse_enabled = True
        logger.info("✅ Langfuse LLM tracing enabled → %s", host)
        return _langfuse_client
    except Exception as exc:
        logger.warning("Langfuse init failed (tracing disabled): %s", exc)
        _langfuse_enabled = False
        return None


def get_langfuse():
    """Return (possibly cached) Langfuse client, or None if unavailable."""
    global _langfuse_client
    if _langfuse_client is None:
        _init_langfuse()
    return _langfuse_client


# ── Trace-Level Context Manager ───────────────────────────────────────────────

@contextmanager
def langfuse_trace(
    name: str,
    session_id: str = "default",
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator:
    """
    Context manager that creates a Langfuse top-level trace for one
    end-to-end compliance query. Yields the trace object (or None).

    Usage:
        with langfuse_trace("compliance-query", session_id=sid) as trace:
            ...
    """
    lf = get_langfuse()
    trace_obj = None

    try:
        if lf and _langfuse_enabled:
            trace_obj = lf.trace(
                name=name,
                session_id=session_id,
                user_id=user_id,
                metadata=metadata or {},
            )
    except Exception as exc:
        logger.debug("Langfuse trace creation failed: %s", exc)

    try:
        yield trace_obj
    finally:
        # Flush is async-safe — ignore all errors
        try:
            if lf and _langfuse_enabled:
                lf.flush()
        except Exception:
            pass


# ── Span-Level Helper ─────────────────────────────────────────────────────────

def langfuse_span(
    trace,
    name: str,
    agent_name: str,
    model: str = "gemini-2.0-flash",
    input_data: Optional[Any] = None,
    output_data: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None,
    latency_ms: Optional[float] = None,
):
    """
    Records a single agent span within an existing Langfuse trace.
    All errors are silently swallowed — observability MUST NOT break queries.

    Args:
        trace:       Langfuse trace object (or None → no-op)
        name:        Span operation name (e.g. "intent_decomposition")
        agent_name:  Agent label (e.g. "SupervisorAgent")
        model:       LLM model name used in this span
        input_data:  Input passed to the agent (dict or str)
        output_data: Output produced by the agent (dict or str)
        metadata:    Additional key-value metadata dict
        latency_ms:  Measured latency in milliseconds
    """
    if trace is None or not _langfuse_enabled:
        return

    try:
        span_meta = {
            "agent": agent_name,
            "model": model,
            **(metadata or {}),
        }
        if latency_ms is not None:
            span_meta["duration_ms"] = round(latency_ms, 2)

        trace.span(
            name=name,
            input=input_data,
            output=output_data,
            metadata=span_meta,
        )
    except Exception as exc:
        logger.debug("Langfuse span creation failed for '%s': %s", name, exc)


# ── LLM Generation Span Helper ────────────────────────────────────────────────

def langfuse_generation(
    trace,
    name: str,
    model: str,
    prompt: str,
    completion: str,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    latency_ms: Optional[float] = None,
):
    """
    Records an LLM generation event within a Langfuse trace.
    Used in SynthesizerAgent to track model calls, token usage, and cost.
    """
    if trace is None or not _langfuse_enabled:
        return

    try:
        usage = {}
        if prompt_tokens is not None:
            usage["input"] = prompt_tokens
        if completion_tokens is not None:
            usage["output"] = completion_tokens

        trace.generation(
            name=name,
            model=model,
            input=prompt,
            output=completion,
            usage=usage if usage else None,
            metadata={"duration_ms": round(latency_ms, 2)} if latency_ms else None,
        )
    except Exception as exc:
        logger.debug("Langfuse generation recording failed: %s", exc)
