import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import logging

from app.core.config import settings
from app.api.pii_shield import redact_pii
from app.services.qdrant_service import search_rbi_clauses, LOADED_CLAUSES, load_documents_corpus
from app.services.semantic_cache import (
    lookup_semantic_cache,
    store_semantic_cache,
    invalidate_semantic_cache,
    CURRENT_CORPUS_VERSION
)
from app.services.citation_validator import (
    validate_citations_deterministically,
    should_abstain_query,
    ABSTAIN_RESPONSE_TEMPLATE
)
from app.services.agents.orchestrator import MultiAgentOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    department: Optional[str] = "compliance"
    session_id: Optional[str] = "default-session"
    circular: Optional[str] = None
    history: Optional[List[Dict[str, Any]]] = None

class Citation(BaseModel):
    circular_no: str
    title: str
    clause: str
    text: str
    score: float
    provenance_hash: Optional[str] = None
    verified: Optional[bool] = True

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    suggested_queries: Optional[List[str]] = []
    pii_redacted: List[str]
    model_used: str
    cached: bool = False
    latency_ms: float = 0.0
    corpus_version: str = CURRENT_CORPUS_VERSION

SYSTEM_PROMPT = """You are BankCompliance AI, the official Banking Regulatory & Compliance Copilot for Indian Scheduled Commercial Banks and NBFCs.
You provide precise, legally auditable interpretations of Reserve Bank of India (RBI) Master Directions, KYC norms, IT Governance, Digital Lending, and Digital Payment regulations.

Rules:
1. Always quote the exact RBI Circular number, Master Direction title, and Section/Clause (e.g. "Under Section 4.2(a) of the RBI Master Direction on KYC...").
2. State clear actionable compliance steps and mandatory statutory penalties for non-compliance.
3. If PII is redacted, explain requirements using sanitized operational language.
4. If the retrieved context is insufficient or conflicting, state so clearly and recommend escalating to the Chief Compliance Officer.
5. Conclude with a recommendation for Bank Internal Audit & Chief Compliance Officer (CCO) review.
"""

@router.post("/compliance/query", response_model=QueryResponse)
async def query_compliance(request: QueryRequest):
    start_time = time.time()

    # 1. PII Redaction
    sanitized_prompt, pii_detected = redact_pii(request.query)

    # 2. Governed Semantic Vector Cache Lookup (FinOps & Sub-10ms Latency)
    cached_result = lookup_semantic_cache(
        query=sanitized_prompt,
        department=request.department or "compliance",
        corpus_version=CURRENT_CORPUS_VERSION
    )

    if cached_result:
        latency = round((time.time() - start_time) * 1000, 2)
        return QueryResponse(
            answer=cached_result["answer"],
            citations=[Citation(**c) for c in cached_result["citations"]],
            pii_redacted=pii_detected,
            model_used=cached_result["model_used"],
            cached=True,
            latency_ms=latency,
            corpus_version=CURRENT_CORPUS_VERSION
        )

    # 3. Multi-Agent Orchestration (Supervisor ➔ Retriever ➔ Auditor ➔ Synthesizer)
    agent_output = await MultiAgentOrchestrator.run(
        sanitized_query=sanitized_prompt,
        department=request.department or "compliance",
        session_id=request.session_id or "default-session",
        history=request.history
    )

    answer = agent_output["answer"]
    model_used = agent_output["model_used"]
    raw_citations = agent_output["citations"]
    suggested_queries = agent_output.get("suggested_queries", [])

    formatted_citations = [
        Citation(
            circular_no=c.get("circular_no", "RBI/Master-Direction"),
            title=c.get("title", "Reserve Bank of India Compliance Framework"),
            clause=c.get("clause", "Regulatory Requirement"),
            text=c.get("text", ""),
            score=c.get("score", 0.95),
            provenance_hash=c.get("provenance_hash", "verified-agent"),
            verified=c.get("verified", True)
        )
        for c in raw_citations
    ]

    # 4. Store in Semantic Cache for Future Instant Retrieval (Only for valid compliance answers)
    if raw_citations:
        store_semantic_cache(
            query=sanitized_prompt,
            answer=answer,
            citations=[c.model_dump() for c in formatted_citations],
            pii_redacted=pii_detected,
            model_used=model_used,
            department=request.department or "compliance",
            corpus_version=CURRENT_CORPUS_VERSION
        )

    latency = round((time.time() - start_time) * 1000, 2)

    return QueryResponse(
        answer=answer,
        citations=formatted_citations,
        suggested_queries=suggested_queries,
        pii_redacted=pii_detected,
        model_used=model_used,
        cached=False,
        latency_ms=latency,
        corpus_version=CURRENT_CORPUS_VERSION
    )

@router.get("/compliance/circulars")
async def list_circulars():
    global LOADED_CLAUSES
    if not LOADED_CLAUSES:
        load_documents_corpus()
        
    seen = set()
    master_directions = []
    
    for c in LOADED_CLAUSES:
        circ_id = c.get("circular_no")
        title = c.get("title")
        if circ_id and circ_id not in seen:
            seen.add(circ_id)
            master_directions.append({
                "id": circ_id,
                "name": title,
                "category": c.get("category", "general_compliance")
            })
            
    return {
        "master_directions": master_directions,
        "corpus_version": CURRENT_CORPUS_VERSION
    }

@router.post("/compliance/ingest")
async def trigger_ingestion():
    """Triggers live ingestion of RBI Master Directions into Qdrant Vector DB."""
    from app.services.data_lake_service import DataLakeService
    result = DataLakeService.ingest_and_index_corpus()
    return result

@router.get("/compliance/stats")
async def get_compliance_stats():
    """Returns real-time Regulatory Data Lake & Qdrant vector statistics."""
    from app.services.data_lake_service import DataLakeService
    return DataLakeService.get_stats()

@router.post("/compliance/cache/invalidate")
async def invalidate_cache_endpoint(new_version: str):
    """Admin endpoint to invalidate semantic cache when new regulations are uploaded."""
    purged = invalidate_semantic_cache(new_version)
    return {
        "status": "success",
        "new_corpus_version": new_version,
        "purged_entries": purged
    }
