"""
BankCompliance AI — Continuous RAG Semantic Drift & Blind-Spot Engine
====================================================================
Implements AI-300 MLOps Production Monitoring for Generative AI & Vector Search:
  1. Tracks sliding-window statistical distribution of retrieval cosine similarity (P10, P50, P90).
  2. Detects 'Silent Drift' when regulatory queries fall outside the document corpus.
  3. Clusters low-confidence queries to automatically identify Corpus Blind Spots.
  4. Generates automated ingestion backlog recommendations for the data engineering pipeline.
"""

import time
import logging
from collections import deque
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("BankCompliance-DriftMonitor")

# Sliding window buffer of recent retrieval queries
WINDOW_SIZE = 100
_QUERY_WINDOW: deque = deque(maxlen=WINDOW_SIZE)

# Thresholds for statistical drift alerting
LOW_CONFIDENCE_THRESHOLD = 0.68
DRIFT_ALERT_RATIO = 0.20  # If >20% queries in the window are low-confidence

def record_retrieval_event(query: str, results: List[Dict[str, Any]]) -> None:
    """Records a retrieval event into the sliding-window drift monitor."""
    scores = [r.get("score", 0.0) for r in results] if results else [0.0]
    max_score = max(scores) if scores else 0.0
    avg_score = sum(scores) / len(scores) if scores else 0.0

    _QUERY_WINDOW.append({
        "query": query,
        "max_score": round(max_score, 4),
        "avg_score": round(avg_score, 4),
        "result_count": len(results),
        "timestamp": time.time(),
        "is_low_confidence": max_score < LOW_CONFIDENCE_THRESHOLD
    })

def get_drift_metrics() -> Dict[str, Any]:
    """
    Computes statistical percentile metrics and drift detection status across the sliding window.
    """
    if not _QUERY_WINDOW:
        return {
            "total_queries_tracked": 0,
            "status": "AWAITING_DATA",
            "rolling_mean_similarity": 0.85,
            "p10_similarity": 0.72,
            "p50_similarity": 0.86,
            "p90_similarity": 0.95,
            "low_confidence_ratio": 0.0,
            "drift_detected": False,
            "corpus_blind_spots": [],
            "ingestion_recommendations": []
        }

    scores = sorted([e["max_score"] for e in _QUERY_WINDOW])
    n = len(scores)
    mean_score = sum(scores) / n

    # Percentiles
    p10 = scores[max(0, int(n * 0.10))]
    p50 = scores[int(n * 0.50)]
    p90 = scores[min(n - 1, int(n * 0.90))]

    low_conf_events = [e for e in _QUERY_WINDOW if e["is_low_confidence"]]
    low_conf_ratio = round(len(low_conf_events) / n, 4)
    drift_detected = low_conf_ratio >= DRIFT_ALERT_RATIO or mean_score < LOW_CONFIDENCE_THRESHOLD

    # Identify blind spots
    blind_spots = []
    recommendations = []
    if low_conf_events:
        words_freq: Dict[str, int] = {}
        for ev in low_conf_events:
            for word in ev["query"].lower().split():
                if len(word) > 3 and word not in {"what", "which", "where", "tell", "under", "about", "bank", "does", "have"}:
                    words_freq[word] = words_freq.get(word, 0) + 1

        top_keywords = sorted(words_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        for kw, cnt in top_keywords:
            blind_spots.append({
                "keyword": kw,
                "occurrences": cnt,
                "mean_retrieval_score": round(sum(e["max_score"] for e in low_conf_events if kw in e["query"].lower()) / max(1, cnt), 3)
            })
            recommendations.append(f"Ingest latest RBI Master Direction addressing topic: '{kw.title()}'")

    status_tag = "CRITICAL_DRIFT" if low_conf_ratio > 0.35 else ("DRIFT_DETECTED" if drift_detected else "HEALTHY")

    return {
        "total_queries_tracked": n,
        "window_capacity": WINDOW_SIZE,
        "status": status_tag,
        "rolling_mean_similarity": round(mean_score, 4),
        "p10_similarity": round(p10, 4),
        "p50_similarity": round(p50, 4),
        "p90_similarity": round(p90, 4),
        "low_confidence_ratio": low_conf_ratio,
        "low_confidence_count": len(low_conf_events),
        "drift_detected": drift_detected,
        "corpus_blind_spots": blind_spots,
        "ingestion_recommendations": recommendations[:3],
        "monitored_at": datetime.now(timezone.utc).isoformat()
    }
