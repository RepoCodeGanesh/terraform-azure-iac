"""
BankCompliance AI — Mathematical Vector Centroid Guardrail (Layer 1)
=====================================================================
Role: Mathematical Vector Domain Sieve (Sub-3ms, Stopword-Filtered Centroid)
Implements:
  1. Stopword-redacted term frequency sparse vector embedding.
  2. Cosine similarity against Normalized Regulatory Knowledge Lake Centroid vector (C_domain).
  3. Maximum clause cosine similarity against indexed RBI Master Direction embeddings.
  4. Automatically incorporates all 12+ multi-domain Master Directions.
"""

import math
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Standard English stopwords to remove noise and prevent non-banking matches
STOPWORDS = {
    'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'in', 'to', 'for', 'of', 'with', 
    'as', 'by', 'from', 'this', 'that', 'it', 'be', 'are', 'was', 'were', 'will', 'can', 'how', 
    'what', 'who', 'when', 'where', 'why', 'do', 'does', 'did', 'have', 'has', 'had', 'should',
    'would', 'could', 'all', 'any', 'some', 'my', 'your', 'our', 'their', 'his', 'her', 'i', 'you',
    'tell', 'explain', 'give', 'about', 'want', 'know', 'please', 'help'
}

# Mathematical thresholds for Stopword-Filtered Multi-Domain Centroid
DOMAIN_SIMILARITY_THRESHOLD = 0.030
MAX_CLAUSE_SIMILARITY_THRESHOLD = 0.060

# Polysemous words with dual financial and common meanings
POLYSEMOUS_WORDS = {'capital', 'interest', 'current', 'charge', 'charges', 'balance', 'statement', 'share', 'shares', 'security', 'branch', 'agent', 'green', 'card'}


def _tokenize(text: str) -> List[str]:
    """Extracts normalized alphanumeric tokens with length > 2, excluding stopwords."""
    words = re.findall(r'[a-zA-Z0-9\-_]+', text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]

def compute_sparse_vector(text: str) -> Dict[str, float]:
    """Computes an L2-normalized term frequency sparse vector embedding without stopwords."""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    tf: Dict[str, float] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0.0) + 1.0
    norm = math.sqrt(sum(v * v for v in tf.values()))
    if norm > 0:
        return {k: v / norm for k, v in tf.items()}
    return tf

def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    """Computes cosine similarity between two normalized sparse vector dictionaries in O(shared_terms)."""
    if not v1 or not v2:
        return 0.0
    # Iterate over the smaller dictionary for speed
    small, large = (v1, v2) if len(v1) < len(v2) else (v2, v1)
    return sum(val * large.get(term, 0.0) for term, val in small.items())

class DomainCentroidGuardrail:
    """Mathematical Domain Centroid Sieve for Indian Banking Compliance."""
    
    _corpus_vectors: List[Dict[str, float]] = []
    _centroid: Dict[str, float] = {}
    _is_initialized: bool = False
    
    @classmethod
    def initialize(cls, corpus_documents: Optional[List[Dict[str, Any]]] = None) -> None:
        """Constructs and normalizes the Regulatory Knowledge Lake Centroid vector in memory across all 12+ domains."""
        docs = corpus_documents or []
        
        if not docs:
            # Dynamically auto-load from the active documents directory
            try:
                from app.services.data_lake_service import DataLakeService
                from app.services.pdf_ingest_service import PDFIngestService
                
                docs_dir = DataLakeService.get_documents_dir()
                for f in docs_dir.glob("*.md"):
                    parsed = PDFIngestService.parse_markdown_document(f)
                    docs.append({
                        "title": parsed.get("title", ""),
                        "text": parsed.get("content", ""),
                        "keywords": [parsed.get("category", ""), parsed.get("circular_no", "")]
                    })
            except Exception as e:
                logger.warning("Could not auto-load documents for centroid: %s", e)
                
        if not docs:
            # Robust fallback representation across 12+ domains
            docs = [
                {"text": "RBI Master Direction Know Your Customer KYC Non-Resident Indian NRI passport visa V-CIP video kyc OVD customer identification aadhaar pan ckyc aml cft periodic updation"},
                {"text": "RBI Master Direction Information Technology Governance cybersecurity data localization cloud commercial public cloud data residues MeitY disaster recovery DR site BCP incident SOC audit"},
                {"text": "RBI Master Direction Outsourcing of Information Technology Services sub-contracting vendor concentration risk CISO compliance audit final credit approval SAS-70 SOC-2 third party"},
                {"text": "RBI Master Direction Digital Payment Security Controls Card-on-File Tokenisation CoFT 16-digit PAN CVV expiry payment aggregator merchant checkout TSP chargeback fraud"},
                {"text": "RBI Master Direction Digital Lending fintech disbursement cooling-off period loan credit recovery agent FLDG first loss default guarantee LSP DLR APR key fact statement lending money debt collection borrowers"},
                {"text": "RBI Master Direction Credit Card Debit Card issuance conduct unsolicited card penalty billing interest rate grievance redressal billing cycle"},
                {"text": "RBI Master Direction Frauds Classification Reporting Central Fraud Registry CFR FMR flash report EWS early warning signals red flagged accounts RFA forensic audit"},
                {"text": "Reserve Bank Integrated Ombudsman Scheme customer grievance redressal complaints 30 days turnaround SLA internal ombudsman zero liability failed transactions compensation"},
                {"text": "RBI Master Direction Basel III Capital Regulations CET1 common equity Tier 1 CRAR capital conservation buffer CCB liquidity coverage ratio LCR NSFR high quality liquid assets"},
                {"text": "RBI Master Direction Liberalised Remittance Scheme LRS FEMA USD 250000 overseas travel education TCS trade export import EDPMS IDPMS foreign exchange"},
                {"text": "RBI Master Direction Prepaid Payment Instruments PPI wallets small PPI full KYC interoperability UPI escrow account co-branding cash loading withdrawal limits"},
                {"text": "RBI Master Direction Safe Deposit Locker safe custody 100 times rent liability theft fire burglary CCTV 180 days SMS alerts inoperative locker break-open"}
            ]
        
        cls._corpus_vectors = [compute_sparse_vector(f"{d.get('title', '')} {d.get('text', '')} {' '.join(d.get('keywords', []))}") for d in docs]
        
        # Calculate unnormalized centroid
        raw_centroid: Dict[str, float] = {}
        for cv in cls._corpus_vectors:
            for term, val in cv.items():
                raw_centroid[term] = raw_centroid.get(term, 0.0) + val
                
        # L2-normalize centroid vector
        norm = math.sqrt(sum(v * v for v in raw_centroid.values()))
        if norm > 0:
            cls._centroid = {k: v / norm for k, v in raw_centroid.items()}
        else:
            cls._centroid = raw_centroid
            
        cls._is_initialized = True
        logger.info("DomainCentroidGuardrail initialized with %d corpus vectors (Centroid dimension: %d)", len(cls._corpus_vectors), len(cls._centroid))
        
    @classmethod
    def evaluate(cls, query: str) -> Tuple[bool, float, float]:
        """
        Mathematically evaluates if a query falls within the Indian Banking & Regulatory Domain.
        Returns:
            (is_in_domain: bool, centroid_similarity: float, max_clause_similarity: float)
        """
        if not cls._is_initialized:
            cls.initialize()
            
        qv = compute_sparse_vector(query)
        if not qv:
            return False, 0.0, 0.0

        centroid_sim = cosine_similarity(qv, cls._centroid)
        max_clause_sim = max((cosine_similarity(qv, cv) for cv in cls._corpus_vectors), default=0.0)

        # Mathematical criterion: In domain if either centroid similarity or any clause similarity meets threshold
        is_in_domain = (centroid_sim >= DOMAIN_SIMILARITY_THRESHOLD) or (max_clause_sim >= MAX_CLAUSE_SIMILARITY_THRESHOLD)

        # Polysemous homonym disambiguation: If query contains ONLY a single polysemous word paired with non-financial terms
        # (e.g., "what is the capital of France" has only 'capital' + 'france'), prevent false positive
        matched_terms = [t for t in qv.keys() if t in cls._centroid]
        if len(matched_terms) == 1 and matched_terms[0] in POLYSEMOUS_WORDS and len(qv) > 1:
            is_in_domain = False

        return is_in_domain, centroid_sim, max_clause_sim



# Initialize on module load
DomainCentroidGuardrail.initialize()


