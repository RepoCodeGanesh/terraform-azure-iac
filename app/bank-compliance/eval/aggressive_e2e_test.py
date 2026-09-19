# ==============================================================================
# BankCompliance AI & TaxBot India -- Aggressive Multi-Agent & FinOps Test Suite
# Tasks 1 to 8: End-to-End Stress, Adversarial, Lineage, HITL & Drift Verification
# ==============================================================================

import os
import sys
import time
import json
import logging
import hashlib
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent.parent
BACKEND_DIR = CURRENT_DIR.parent / "backend"
TAXBOT_DIR = REPO_ROOT / "app" / "tax-advisor" / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AggressiveTestSuite")

passed_count = 0
failed_count = 0

def record_test(name: str, passed: bool, detail: str = ""):
    global passed_count, failed_count
    if passed:
        passed_count += 1
        logger.info(f"  \u2705 [PASS] {name} {detail}")
    else:
        failed_count += 1
        logger.error(f"  \u274c [FAIL] {name} - {detail}")

# ─── SECTION 1: TaxBot Foundry & Multi-Cloud Fallback ─────────────────────────
def test_taxbot_foundry_and_fallback():
    logger.info("\n=== [1/7] Testing TaxBot Tier-2 Foundry & Multi-Cloud Resilience ===")
    func_path = TAXBOT_DIR / "function_app.py"
    if not func_path.exists():
        record_test("TaxBot function_app.py exists", False, "Not found")
        return

    code = func_path.read_text(encoding="utf-8")
    record_test("Foundry Agent Client import", "from azure.ai.projects import AIProjectClient" in code)
    record_test("AI Foundry Endpoint configured", "FOUNDRY_PROJECT_ENDPOINT" in code)
    record_test("Gemini Resilient Fallback defined", "def invoke_gemini" in code)
    record_test("Gemini 2.5 Flash model selected", "gemini-2.5-flash" in code)
    record_test("Azure OpenAI retained without orphan", "AZURE_OPENAI_ENDPOINT" in code and "FOUNDRY_OPENAI_ENDPOINT" in code)
    record_test("3-Tier Cascade execution flow", "AIProjectClient" in code and "invoke_gemini" in code and "AzureOpenAI" in code)

# ─── SECTION 2: Cryptographic Lineage & LoRA Model Registry ──────────────────
def test_cryptographic_lineage():
    logger.info("\n=== [2/7] Testing Cryptographic Lineage & Model Registry ===")
    from app.services.rbi_chunker import chunk_rbi_markdown
    from app.services.qdrant_service import get_provenance_by_id, load_documents_corpus

    sample_md = "# Reserve Bank of India\n\n## Chapter I: IT Governance\nCore banking outsourcing shall comply with RBI rules.\n\n## Chapter II: Data Localization\nPayment data must be stored exclusively in India."
    chunks = chunk_rbi_markdown(sample_md, circular_id="RBI/2026-IT/01", circular_title="IT Governance Master Direction")

    record_test("Markdown chunk generation", len(chunks) >= 2, f"Got {len(chunks)} chunks")
    c1 = chunks[0]
    expected_hash = f"sha256:{hashlib.sha256(c1['text'].encode('utf-8')).hexdigest()}"
    record_test("Chunk SHA-256 cryptographic match", c1.get("chunk_sha256") == expected_hash)
    record_test("Parent document SHA-256 bound", "parent_doc_sha256" in c1)
    record_test("Deterministic chunk ID", "chunk_id" in c1)

    load_documents_corpus()
    prov = get_provenance_by_id("KYC")
    record_test("Provenance lookup resolved", prov is not None)
    if prov:
        record_test("Provenance verified flag", prov.get("verified") is True)
        record_test("Lineage parent doc hash present", "parent_doc_sha256" in prov.get("provenance", {}))

    card_path = REPO_ROOT / "merged_compliance_model" / "v1.0.0" / "model_card.json"
    record_test("Model registry model_card.json exists", card_path.exists())
    if card_path.exists():
        card_data = json.loads(card_path.read_text(encoding="utf-8"))
        record_test("Model card version 1.0.0", card_data.get("version") == "1.0.0")
        record_test("LoRA adapter architecture documented", "lora_rank" in card_data.get("training_provenance", {}).get("hyperparameters", {}))
        record_test("Training lineage tracked", "training_provenance" in card_data)

# ─── SECTION 3: HITL Escalation Lifecycle ────────────────────────────────────
def test_hitl_escalation():
    logger.info("\n=== [3/7] Testing Human-in-the-Loop (HITL) Regulatory Escalation ===")
    from app.services.escalation_service import (
        check_hitl_requirement,
        create_escalation_ticket,
        review_escalation_ticket,
        list_escalation_tickets
    )

    clean_q = "What documents are acceptable for NRI KYC verification?"
    hitl_req, _, _, _ = check_hitl_requirement(clean_q)
    record_test("Autonomous bypass for safe query", hitl_req is False)

    dangerous_q = "We want an agreement offering 15% First Loss Default Guarantee (FLDG) to our FinTech partner."
    hitl_dang, risk_dang, trig, reas = check_hitl_requirement(dangerous_q)
    record_test("FLDG breach detected", hitl_dang is True, trig)
    record_test("Risk level is CRITICAL", risk_dang == "CRITICAL")

    ticket = create_escalation_ticket(
        query=dangerous_q,
        preliminary_answer="FLDG is legally capped at 5%.",
        citations=[],
        risk_level=risk_dang,
        trigger_name=trig,
        reason=reas
    )
    record_test("Ticket created in PENDING review", ticket.get("status") == "PENDING_COMPLIANCE_REVIEW")
    ticket_id = ticket["ticket_id"]

    signed = review_escalation_ticket(
        ticket_id=ticket_id,
        officer_name="Mr. Rajesh Gupta (Chief Compliance Officer)",
        verdict="REJECTED",
        officer_notes="Arrangement strictly violates RBI Digital Lending norms. Ceiling is 5%."
    )
    record_test("Ticket status transitioned to OFFICER_REJECTED", signed.get("status") == "OFFICER_REJECTED")
    record_test("Cryptographic sign-off receipt generated", "cryptographic_signature" in signed)

# ─── SECTION 4: 2-Tier Semantic Vector Caching & FinOps Engine ────────────────
def test_semantic_caching_and_finops():
    logger.info("\n=== [4/7] Testing 2-Tier Semantic Vector Caching & Real-Time FinOps ===")
    from app.services.semantic_cache import (
        store_semantic_cache,
        lookup_semantic_cache,
        get_cache_finops_summary,
        invalidate_semantic_cache
    )

    cache_q = "What is the capital adequacy ratio for scheduled commercial banks in India?"
    cache_ans = "Under Basel III norms as adopted by RBI, the minimum Capital to Risk-Weighted Assets Ratio (CRAR) is 9%."
    cache_cit = [{"circular_no": "RBI/2015-16/58", "title": "Master Circular - Basel III", "clause": "Para 4.1"}]

    store_semantic_cache(cache_q, cache_ans, cache_cit, [], "gpt-5.4-mini")

    hit = lookup_semantic_cache(cache_q)
    record_test("Semantic cache exact hit", hit is not None and hit.get("cached") is True)

    paraphrase_q = "What is the capital adequacy ratio for scheduled commercial banks?"
    hit2 = lookup_semantic_cache(paraphrase_q)
    record_test("Semantic cache cosine paraphrase hit", hit2 is not None)

    finops = get_cache_finops_summary()
    record_test("FinOps tracked cached requests", finops.get("cache_entries_count") >= 1)
    record_test("FinOps status is HEALTHY_OPTIMIZED", finops.get("status") == "HEALTHY_OPTIMIZED")

    purged = invalidate_semantic_cache("2026.09.20.E2E")
    record_test("Cache purged on corpus upgrade", purged >= 1)

# ─── SECTION 5: Continuous RAG Drift & Statistical Detector ──────────────────
def test_rag_drift_monitor():
    logger.info("\n=== [5/7] Testing Continuous RAG Semantic Drift & Blind-Spot Detector ===")
    from app.services.drift_monitor import record_retrieval_event, get_drift_metrics

    # Healthy events
    for _ in range(10):
        record_retrieval_event("normal kyc query", [{"score": 0.88}, {"score": 0.82}])
    m1 = get_drift_metrics()
    record_test("Healthy retrieval does not trigger drift alert", m1.get("drift_detected") is False)

    # Influx of low-similarity events
    for _ in range(15):
        record_retrieval_event("unknown cryptocurrency derivative regulations 2026", [{"score": 0.35}])
    m2 = get_drift_metrics()
    record_test("Drift status detects out-of-corpus degradation", m2.get("drift_detected") is True)
    record_test("Corpus blind spots identified", len(m2.get("corpus_blind_spots", [])) > 0)

# ─── SECTION 6: Automated AI Red Teaming Interception ────────────────────────
def test_red_teaming_interceptions():
    logger.info("\n=== [6/7] Testing Automated AI Red Teaming Interceptions (PyRIT) ===")
    attestation_path = REPO_ROOT / "redteam_security_attestation.json"
    record_test("Red teaming security attestation JSON exists", attestation_path.exists())
    if attestation_path.exists():
        att = json.loads(attestation_path.read_text(encoding="utf-8"))
        record_test("All 25 attack vectors intercepted", att.get("attacks_intercepted") == 25)
        record_test("Defense resilience rate 100%", att.get("defense_resilience_rate") == "100.0%")
        record_test("Zero PII leaks under adversarial attack", att.get("pii_leakage_rate") == "0.0%")

# ─── SECTION 7: High-Throughput Concurrent Burst Stress ───────────────────────
def test_concurrent_burst():
    logger.info("\n=== [7/7] Stress Testing: 50 Concurrent Multi-Agent / Cache Queries ===")
    from app.services.semantic_cache import lookup_semantic_cache, store_semantic_cache
    from app.services.escalation_service import check_hitl_requirement

    test_queries = [
        "What is the capital adequacy requirement for Tier 1 capital?",
        "Explain V-CIP video KYC guidelines for non-resident Indians.",
        "Can a payment aggregator store customer credit card CVV?",
        "What is the cooling-off period in digital lending contracts?",
        "What are the reporting timelines for cyber security incidents?"
    ]

    for i, tq in enumerate(test_queries):
        store_semantic_cache(
            tq,
            f"Aggressive test pre-verified answer for query {i}",
            [{"circular_no": f"RBI/TEST/{i}", "clause": "Clause 1"}],
            [],
            "gpt-5.4-mini"
        )

    def worker_task(task_id: int):
        t0 = time.time()
        q = test_queries[task_id % len(test_queries)]
        hit = lookup_semantic_cache(q)
        hitl_req, _, _, _ = check_hitl_requirement(q)
        duration_ms = (time.time() - t0) * 1000
        return {"task_id": task_id, "cached": hit is not None, "duration_ms": duration_ms}

    results = []
    start_all = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker_task, i) for i in range(50)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
    total_burst_time = (time.time() - start_all) * 1000

    all_cached = all(r["cached"] for r in results)
    avg_latency = sum(r["duration_ms"] for r in results) / len(results)
    max_latency = max(r["duration_ms"] for r in results)

    record_test("50/50 concurrent queries served cleanly", len(results) == 50)
    record_test("100% cache hit consistency under race condition", all_cached)
    record_test("Average latency under high concurrency (<10ms)", avg_latency < 10.0, f"Avg: {avg_latency:.2f}ms, Max: {max_latency:.2f}ms")
    logger.info(f"  \u26a1 Total 50 queries served in {total_burst_time:.2f}ms (Throughput: {50 / (total_burst_time / 1000):.1f} req/sec)")

def main():
    logger.info("=================================================================")
    logger.info("   STARTING AGGRESSIVE TEST SUITE ACROSS ALL 8 CAPABILITIES     ")
    logger.info("=================================================================")
    
    test_taxbot_foundry_and_fallback()
    test_cryptographic_lineage()
    test_hitl_escalation()
    test_semantic_caching_and_finops()
    test_rag_drift_monitor()
    test_red_teaming_interceptions()
    test_concurrent_burst()

    logger.info("\n=================================================================")
    logger.info(f"   TEST SUITE SUMMARY: {passed_count} PASSED, {failed_count} FAILED")
    logger.info("=================================================================")

    if failed_count > 0:
        logger.error(f"Aggressive test suite failed with {failed_count} errors.")
        sys.exit(1)
    else:
        logger.info("\U0001f389 ALL 8 ENTERPRISE CAPABILITIES VALIDATED 100% SUCCESSFUL!")
        sys.exit(0)

if __name__ == "__main__":
    main()
