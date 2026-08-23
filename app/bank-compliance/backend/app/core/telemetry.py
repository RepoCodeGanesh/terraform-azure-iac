"""
BankCompliance AI — OpenTelemetry GenAI Standard Distributed Tracing
=====================================================================
Implements OpenTelemetry GenAI Semantic Conventions (v1.26+) for end-to-end
multi-agent distributed tracing, token metering, and latency observability.
"""

import time
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional, Generator

logger = logging.getLogger("BankCompliance-OTel")

class GenAISpan:
    """Represents an active OpenTelemetry GenAI tracing span."""

    def __init__(self, operation_name: str, agent_name: str, model_name: Optional[str] = None):
        self.operation_name = operation_name
        self.agent_name = agent_name
        self.model_name = model_name or "gemini-2.0-flash"
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0
        self.attributes: Dict[str, Any] = {
            "gen_ai.system": "bank_compliance_ai",
            "gen_ai.agent.name": agent_name,
            "gen_ai.operation.name": operation_name,
            "gen_ai.request.model": self.model_name,
            "gen_ai.span.kind": "INTERNAL"
        }
        self.events: list = []

    def set_attribute(self, key: str, value: Any) -> None:
        """Sets a GenAI semantic attribute."""
        self.attributes[key] = value

    def record_token_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Records token usage according to OTel GenAI conventions."""
        self.attributes["gen_ai.usage.prompt_tokens"] = prompt_tokens
        self.attributes["gen_ai.usage.completion_tokens"] = completion_tokens
        self.attributes["gen_ai.usage.total_tokens"] = prompt_tokens + completion_tokens

    def record_event(self, name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Records an event within the span."""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "payload": payload or {}
        })

    def end(self, status: str = "OK", error: Optional[str] = None) -> Dict[str, Any]:
        """Closes the span and computes duration."""
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.attributes["gen_ai.status"] = status
        self.attributes["gen_ai.duration_ms"] = self.duration_ms
        if error:
            self.attributes["gen_ai.error"] = str(error)

        logger.debug(
            "OTel Span [%s][%s] completed in %.2f ms (Status: %s)",
            self.agent_name, self.operation_name, self.duration_ms, status
        )
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation_name,
            "agent": self.agent_name,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events_count": len(self.events)
        }

@contextmanager
def trace_agent_span(
    operation_name: str,
    agent_name: str,
    model_name: Optional[str] = None
) -> Generator[GenAISpan, None, None]:
    """Context manager for tracing individual agent operations."""
    span = GenAISpan(operation_name, agent_name, model_name)
    try:
        yield span
        span.end(status="OK")
    except Exception as e:
        span.end(status="ERROR", error=str(e))
        raise
