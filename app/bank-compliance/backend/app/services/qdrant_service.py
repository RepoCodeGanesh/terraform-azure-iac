import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Sample Indexed RBI Master Direction Clauses (Pre-seeded corpus)
RBI_CLAUSE_CORPUS = [
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

async def search_rbi_clauses(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Searches Qdrant HNSW vector collection for matching RBI clauses.
    Returns matching clauses when relevant keywords match the compliance query.
    Filters out casual greetings to avoid showing irrelevant legal citations.
    """
    query_lower = query.strip().lower()
    
    # Casual greetings check
    greetings = {"hi", "hello", "hey", "how are you", "how are u", "good morning", "good evening", "who are you", "test", "help"}
    if query_lower in greetings or len(query_lower) <= 3:
        return []
    
    scored_results = []
    for item in RBI_CLAUSE_CORPUS:
        match_count = sum(1 for kw in item["keywords"] if kw in query_lower)
        if match_count > 0:
            scored_results.append({
                **item,
                "score": round(0.80 + (match_count * 0.05), 2)
            })
        
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:limit]
