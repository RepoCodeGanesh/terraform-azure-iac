"""
BankCompliance AI — Multi-Agent State Definition
=================================================
Defines the shared typed state dictionary exchanged across
Planner, Retriever, Auditor, and Synthesizer agents.
"""

from typing import TypedDict, List, Dict, Any, Optional

class CitationEvidence(TypedDict):
    circular_no: str
    title: str
    clause: str
    text: str
    score: float
    provenance_hash: Optional[str]
    verified: bool

class AgentExecutionState(TypedDict):
    original_query: str
    sanitized_query: str
    department: str
    session_id: str
    
    # Planner outputs (Gemini 2.0 Flash-Lite)
    sub_tasks: List[str]
    identified_domains: List[str]
    
    # Retriever outputs (text-embedding-004 + Qdrant)
    retrieved_evidence: List[Dict[str, Any]]
    
    # Auditor / Reflection outputs (Gemini 2.0 Flash-Thinking)
    audit_passed: bool
    audit_feedback: List[str]
    iteration_count: int
    
    # Final Synthesizer output (Gemini 2.0 Flash / Azure OpenAI Fallback)
    final_answer: str
    citations: List[Dict[str, Any]]
    model_used: str
