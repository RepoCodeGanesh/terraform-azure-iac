from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx

from app.core.config import settings
from app.api.pii_shield import redact_pii
from app.services.qdrant_service import search_rbi_clauses

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    department: Optional[str] = "compliance"
    session_id: Optional[str] = "default-session"

class Citation(BaseModel):
    circular_no: str
    title: str
    clause: str
    text: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    pii_redacted: List[str]
    model_used: str

SYSTEM_PROMPT = """You are BankCompliance AI, the official Banking Regulatory & Compliance Copilot for Indian Scheduled Commercial Banks and NBFCs.
You provide precise, legally auditable interpretations of Reserve Bank of India (RBI) Master Directions, KYC norms, IT Governance, and Digital Payment regulations.

Rules:
1. Always quote the exact RBI Circular number, Master Direction, and Section/Clause (e.g. "Under Section 4.2(a) of the RBI Master Direction on KYC...").
2. State clear actionable compliance steps and mandatory penalties for non-compliance.
3. If PII is redacted, explain requirements using sanitized operational language.
4. Conclude with a recommendation for Bank Internal Audit & Chief Compliance Officer (CCO) review.
"""

@router.post("/compliance/query", response_model=QueryResponse)
async def query_compliance(request: QueryRequest):
    # 1. PII Redaction
    sanitized_prompt, pii_detected = redact_pii(request.query)
    
    # 2. Qdrant Vector Retrieval
    retrieved_clauses = await search_rbi_clauses(sanitized_prompt, limit=3)
    
    context_text = "\n\n".join([
        f"--- [{c['circular_no']} - {c['clause']}] ---\n{c['text']}"
        for c in retrieved_clauses
    ])
    
    # 3. Call LiteLLM Proxy Gateway
    user_message = f"Relevant RBI Master Direction Context:\n{context_text}\n\nCompliance Officer Question:\n{sanitized_prompt}"
    
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
                    "temperature": 0.1,
                    "max_tokens": 800,
                    "user": f"{request.department}:{request.session_id}"
                }
            )
            resp.raise_for_status()
            ai_data = resp.json()
            answer = ai_data["choices"][0]["message"]["content"]
    except Exception as e:
        # Fallback response if LiteLLM is not running locally
        answer = f"Based on retrieved RBI Master Directions:\n\n{context_text}\n\n*(Note: Gateway returned: {str(e)})*"

    citations = [
        Citation(
            circular_no=c["circular_no"],
            title=c["title"],
            clause=c["clause"],
            text=c["text"],
            score=c.get("score", 0.95)
        )
        for c in retrieved_clauses
    ]

    return QueryResponse(
        answer=answer,
        citations=citations,
        pii_redacted=pii_detected,
        model_used=settings.OPENAI_MODEL
    )

@router.get("/compliance/circulars")
async def list_circulars():
    return {
        "master_directions": [
            {"id": "RBI/2016-17/KYC", "name": "Master Direction - Know Your Customer (KYC)", "year": 2026},
            {"id": "RBI/2023-24/IT-GOV", "name": "Master Direction - IT Governance & Cybersecurity", "year": 2024},
            {"id": "RBI/2023-24/OUTSOURCING", "name": "Master Direction - Outsourcing of IT Services", "year": 2023},
            {"id": "RBI/2022-23/CARDS", "name": "Master Direction - Credit and Debit Card Issuance", "year": 2025},
            {"id": "RBI/2021-22/DIGITAL-PAY", "name": "Master Direction - Digital Payment Security Controls", "year": 2024}
        ]
    }
