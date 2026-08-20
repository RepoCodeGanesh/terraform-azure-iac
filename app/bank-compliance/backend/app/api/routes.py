import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    department: Optional[str] = "compliance"
    session_id: Optional[str] = "default-session"
    circular: Optional[str] = None

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

    # 3. Qdrant Vector / Semantic Retrieval across Active Regulatory Corpus
    raw_clauses = await search_rbi_clauses(sanitized_prompt, limit=3)

    # 4. Deterministic Citation Validation & Evidence Check
    validated_citations, is_valid_evidence = validate_citations_deterministically(
        raw_clauses,
        LOADED_CLAUSES or load_documents_corpus()
    )

    # 5. Abstain / Escalate Policy Check
    if not is_valid_evidence or should_abstain_query(sanitized_prompt, raw_clauses):
        latency = round((time.time() - start_time) * 1000, 2)
        return QueryResponse(
            answer=ABSTAIN_RESPONSE_TEMPLATE,
            citations=[],
            pii_redacted=pii_detected,
            model_used="governance-policy-abstain",
            cached=False,
            latency_ms=latency,
            corpus_version=CURRENT_CORPUS_VERSION
        )

    context_text = "\n\n".join([
        f"--- [{c['circular_no']} - {c['clause']} (SHA: {c.get('provenance_hash', 'verified')})] ---\n{c['text']}"
        for c in validated_citations
    ])
    user_message = f"Relevant RBI Master Direction Context:\n{context_text}\n\nCompliance Officer Question:\n{sanitized_prompt}"

    # 6. Call LiteLLM Proxy Gateway (Gemini 2.0 Flash ➔ Azure OpenAI Fallback)
    model_used = settings.OPENAI_MODEL
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.LITELLM_URL}/chat/completions",
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    "max_completion_tokens": 800,
                    "user": f"{request.department}:{request.session_id}"
                }
            )
            resp.raise_for_status()
            ai_data = resp.json()
            answer = ai_data["choices"][0]["message"]["content"]
            model_used = ai_data.get("model", settings.OPENAI_MODEL)
    except Exception as e:
        logger.warning(f"LiteLLM Gateway call exception ({e}), generating grounded fallback response.")
        answer = (
            f"**Statutory Position (Grounded Regulatory Extract):**\n\n"
            f"{context_text}\n\n"
            f"*Mandatory Action:* Verify operational implementation with internal audit."
        )
        model_used = "grounded-fallback"

    formatted_citations = [
        Citation(
            circular_no=c["circular_no"],
            title=c["title"],
            clause=c["clause"],
            text=c["text"],
            score=c.get("score", 0.95),
            provenance_hash=c.get("provenance_hash"),
            verified=True
        )
        for c in validated_citations
    ]

    # 7. Store in Semantic Cache for Future Instant Retrieval
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

@router.post("/compliance/cache/invalidate")
async def invalidate_cache_endpoint(new_version: str):
    """Admin endpoint to invalidate semantic cache when new regulations are uploaded."""
    purged = invalidate_semantic_cache(new_version)
    return {
        "status": "success",
        "new_corpus_version": new_version,
        "purged_entries": purged
    }
