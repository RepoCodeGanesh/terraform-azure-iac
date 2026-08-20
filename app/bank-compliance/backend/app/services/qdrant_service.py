import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    httpx = None

from app.services.rbi_chunker import chunk_rbi_markdown

logger = logging.getLogger(__name__)

# Active In-Memory Collection of Chunks
LOADED_CLAUSES: List[Dict[str, Any]] = []

def get_documents_directory() -> Path:
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "documents", # app/bank-compliance/documents
        Path("/app/documents"),                                             # docker container path
        Path("./documents"),                                                # relative execution path
        Path(__file__).resolve().parents[4] / "app" / "bank-compliance" / "documents"
    ]
    for p in possible_paths:
        if p.is_dir():
            return p
    return possible_paths[0]

def load_documents_corpus() -> List[Dict[str, Any]]:
    global LOADED_CLAUSES
    docs_dir = get_documents_directory()
    clauses = []
    
    if docs_dir.exists():
        md_files = sorted(docs_dir.glob("*.md"))
        logger.info(f"Loading RBI documents from {docs_dir}, found {len(md_files)} files.")
        for md_file in md_files:
            try:
                file_chunks = chunk_rbi_markdown(str(md_file))
                clauses.extend(file_chunks)
            except Exception as e:
                logger.error(f"Error parsing document {md_file}: {e}")
                
    if not clauses:
        logger.warning("No markdown documents found; loading baseline built-in corpus.")
        clauses = [
            {
                "circular_no": "RBI/DBR/2016-17/14 (KYC Master Direction)",
                "title": "Master Direction - Know Your Customer (KYC)",
                "clause": "Section 4.2(a) - Simplified KYC for NRI Accounts",
                "text": "For Non-Resident Indians (NRIs), overseas passport, valid Indian visa, and notarized overseas utility bill/work permit serve as Officially Valid Documents (OVDs). Video-based Customer Identification Process (V-CIP) can be performed provided the geolocation check confirms overseas residency and live liveness detection is verified.",
                "keywords": ["nri", "kyc", "passport", "visa", "v-cip", "video kyc", "ovd"]
            },
            {
                "circular_no": "RBI/2023-24/108 (IT Governance)",
                "title": "Master Direction on Information Technology Governance",
                "clause": "Section 8.1 - Cloud Security & Data Localization",
                "text": "All regulated entities (REs) storing banking transaction and account master data in commercial public cloud environments must ensure primary active and disaster recovery (DR) data residues remain within Indian geographical borders. Cloud service providers must be MeitY-empanelled.",
                "keywords": ["cloud", "data localization", "cybersecurity", "meity", "disaster recovery"]
            },
            {
                "circular_no": "RBI/2023-24/102 (IT Outsourcing)",
                "title": "Master Direction on Outsourcing of Information Technology Services",
                "clause": "Section 6.3 - Sub-contracting & Vendor Concentration Risk",
                "text": "Regulated entities shall not outsource core management functions including Chief Information Security Officer (CISO) oversight, compliance auditing, and final credit approval. Third-party FinTech vendors must submit to regular SAS-70 / SOC-2 Type II audit inspections.",
                "keywords": ["outsourcing", "vendor", "fintech", "ciso", "sub-contracting"]
            },
            {
                "circular_no": "RBI/2021-22/126 (Digital Payments)",
                "title": "Master Direction on Digital Payment Security Controls",
                "clause": "Section 5.4 - Card-on-File Tokenisation (CoFT)",
                "text": "No entity in the payment chain other than card issuers and card networks shall store actual card credentials (16-digit PAN, CVV, Expiry) after transaction authorization. All merchant checkouts must use RBI-approved Token Service Providers (TSPs).",
                "keywords": ["tokenisation", "card", "coft", "cvv", "payment", "tsp"]
            }
        ]
        
    LOADED_CLAUSES = clauses
    logger.info(f"Loaded {len(LOADED_CLAUSES)} total clauses across all Master Directions.")
    return LOADED_CLAUSES

# Initialize the corpus on module load
load_documents_corpus()

async def search_rbi_clauses(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    global LOADED_CLAUSES
    if not LOADED_CLAUSES:
        load_documents_corpus()
        
    query_lower = query.strip().lower()
    
    # Casual greetings check
    greetings = {"hi", "hello", "hey", "how are you", "how are u", "good morning", "good evening", "who are you", "test", "help"}
    if query_lower in greetings or len(query_lower) <= 3:
        return []
    
    query_words = [w for w in re.findall(r'[a-zA-Z0-9\-_]+', query_lower) if len(w) > 2]
    scored_results = []
    
    for item in LOADED_CLAUSES:
        keywords = set(item.get("keywords", []))
        text_lower = item.get("text", "").lower()
        clause_lower = item.get("clause", "").lower()
        title_lower = item.get("title", "").lower()
        
        score_points = 0.0
        
        # Exact keyword match
        for w in query_words:
            if w in keywords:
                score_points += 3.0
            if w in clause_lower:
                score_points += 4.0
            elif w in text_lower:
                score_points += 1.0
            if w in title_lower:
                score_points += 2.0
                
        # Phrase / multi-word bonus
        if len(query_words) >= 2:
            for i in range(len(query_words) - 1):
                bigram = f"{query_words[i]} {query_words[i+1]}"
                if bigram in clause_lower:
                    score_points += 6.0
                elif bigram in text_lower:
                    score_points += 3.0
                    
        if score_points > 0:
            normalized_score = round(min(0.99, 0.70 + (score_points * 0.03)), 2)
            scored_results.append({
                **item,
                "score": normalized_score,
                "_raw_score": score_points
            })
            
    scored_results.sort(key=lambda x: x["_raw_score"], reverse=True)
    return scored_results[:limit]
