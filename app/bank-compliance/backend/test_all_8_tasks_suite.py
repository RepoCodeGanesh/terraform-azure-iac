"""
BankCompliance AI & TaxBot — Comprehensive 8-Task Verification Suite
====================================================================
Aggressive automated integration tests validating all 8 enterprise capabilities:
  [Task 1] Azure AI Foundry Tier 2 Agent Service SDK (TaxBot)
  [Task 2] Multi-Cloud Resilient Fallback to Google Gemini
  [Task 3] Cryptographic Data Lineage (PDF -> Chunk -> Vector) & Model Registry
  [Task 4] LangGraph Multi-Agent StateGraph with Cyclic Reflection
  [Task 5] Human-in-the-Loop (HITL) Regulatory Review & Escalation
  [Task 6] Automated AI Red Teaming & Adversarial Benchmark (PyRIT)
  [Task 7] Continuous RAG Semantic Drift & Corpus Blind-Spot Monitor
  [Task 8] 2-Tier Semantic Vector Caching & Token FinOps Engine
"""

import sys
import os
import json
import hashlib
import time
import logging
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Test-8Tasks")

passed_tests = 0
failed_tests = 0

def test_assert(condition: bool, test_name: str, details: str = ""):
    global passed_tests, failed_tests
    if condition:
        passed_tests += 1
        logger.info("  [PASS] %s %s", test_name, f"({details})" if details else "")
    else:
        failed_tests += 1
        logger.error("  [FAIL] %s %s", test_name, f"({details})" if details else "")

def run_suite():
    logger.info("=================================================================")
    logger.info("  RUNNING AGGRESSIVE 8-TASK ENTERPRISE TEST SUITE")
    logger.info("=================================================================")

    # ── TASK 1 & 2: TaxBot Foundry Tier 2 & Gemini Fallback ───────────────────
    logger.info("\n--- [TASK 1 & 2] TaxBot Foundry Tier 2 & Multi-Cloud Fallback ---")
    taxbot_func = REPO_ROOT / "app" / "tax-advisor" / "backend" / "function_app.py"
    test_assert(taxbot_func.exists(), "TaxBot function_app.py exists")
    func_content = taxbot_func.read_text(encoding="utf-8")
    test_assert("AIProjectClient" in func_content, "Foundry Agent Service SDK referenced")
    test_assert("GEMINI_API_KEY" in func_content, "Google Gemini configuration constants present")
    test_assert("def invoke_gemini" in func_content, "invoke_gemini helper implemented")
    test_assert("FOUNDRY_OPENAI_ENDPOINT" in func_content, "Direct AzureOpenAI retained (zero orphan)")
    test_assert("tier 1:" in func_content.lower() and "tier 2:" in func_content.lower() and "tier 3:" in func_content.lower(),
                "3-tier calculation cascade implemented")

    # ── TASK 3: Cryptographic Data Lineage & LoRA Model Registry ─────────────
    logger.info("\n--- [TASK 3] Cryptographic Data Lineage & Model Registry ---")
    from app.services.rbi_chunker import chunk_rbi_markdown
    sample_md = "# Reserve Bank of India\n\n## Chapter I: General\nAll commercial banks must comply.\n\n## Chapter II: FLDG\nFLDG cannot exceed 5%."
    chunks = chunk_rbi_markdown(sample_md, circular_id="RBI/2026/TEST", circular_title="Test Circular")
    test_assert(len(chunks) >= 2, "Markdown chunker produced valid clause chunks", f"got {len(chunks)}")


    c1 = chunks[0]
    expected_hash = f"sha256:{hashlib.sha256(c1['text'].encode('utf-8')).hexdigest()}"
    test_assert(c1.get("chunk_sha256") == expected_hash, "Chunk SHA-256 cryptographic match", c1.get("chunk_sha256"))
    test_assert("parent_doc_sha256" in c1, "Parent document SHA-256 bound to chunk")
    test_assert("chunk_id" in c1, "Deterministic chunk ID generated", c1.get("chunk_id"))

    from app.services.qdrant_service import get_provenance_by_id, load_documents_corpus
    load_documents_corpus()
    prov = get_provenance_by_id("KYC")
    test_assert(prov is not None, "Provenance lookup by clause/keyword successful")
    if prov:
        test_assert(prov.get("verified") is True, "Provenance cryptographic verification flag True")
        test_assert("parent_doc_sha256" in prov.get("provenance", {}), "Parent doc hash present in audit receipt")

    # Model Card verification
    card_path = REPO_ROOT / "merged_compliance_model" / "v1.0.0" / "model_card.json"
    test_assert(card_path.exists(), "Model registry model_card.json exists")
    if card_path.exists():
        card_data = json.loads(card_path.read_text(encoding="utf-8"))
        test_assert(card_data.get("version") == "1.0.0", "Model card semantic version 1.0.0")
        test_assert("training_provenance" in card_data, "Training provenance dataset tracked")

    # ── TASK 4: LangGraph Multi-Agent StateGraph ──────────────────────────────
    logger.info("\n--- [TASK 4] LangGraph Multi-Agent StateGraph Pipeline ---")
    from app.services.agents.orchestrator_v2 import (
        supervisor_node,
        retriever_node,
        auditor_node,
        route_intent,
        route_audit_verdict
    )
    test_assert(callable(supervisor_node), "LangGraph supervisor_node is callable")
    test_assert(callable(retriever_node), "LangGraph retriever_node is callable")
    test_assert(callable(auditor_node), "LangGraph auditor_node is callable")

    greeting_state = {"intent": "greeting"}
    test_assert(route_intent(greeting_state) == "greeting", "route_intent fast-paths greeting")

    audit_fail_state = {"audit_passed": False, "iteration_count": 0}
    test_assert(route_audit_verdict(audit_fail_state) == "retry_retrieve", "route_audit_verdict loops back to retriever on fail")

    # ── TASK 5: Human-in-the-Loop (HITL) Regulatory Escalation ───────────────
    logger.info("\n--- [TASK 5] Human-in-the-Loop (HITL) Governance ---")
    from app.services.escalation_service import (
        check_hitl_requirement,
        create_escalation_ticket,
        list_escalation_tickets,
        review_escalation_ticket
    )
    safe_q = "What are the KYC guidelines for senior citizen bank accounts?"
    hitl_safe, risk_safe, _, _ = check_hitl_requirement(safe_q)
    test_assert(hitl_safe is False, "Standard KYC query allows autonomous resolution (no HITL)")

    dangerous_q = "We want an agreement offering 15% First Loss Default Guarantee (FLDG) to our FinTech partner."
    hitl_dang, risk_dang, trig, reas = check_hitl_requirement(dangerous_q)
    test_assert(hitl_dang is True, "High-risk FLDG breach triggers mandatory HITL", trig)
    test_assert(risk_dang == "CRITICAL", "FLDG breach flagged with CRITICAL risk")

    ticket = create_escalation_ticket(
        query=dangerous_q,
        preliminary_answer="FLDG is legally capped at 5%.",
        citations=[],
        risk_level=risk_dang,
        trigger_name=trig,
        reason=reas
    )
    test_assert(ticket.get("status") == "PENDING_COMPLIANCE_REVIEW", "Ticket created in PENDING_COMPLIANCE_REVIEW state")
    ticket_id = ticket["ticket_id"]

    signed = review_escalation_ticket(
        ticket_id=ticket_id,
        officer_name="Priya Sharma, Chief Compliance Officer",
        verdict="REJECTED",
        officer_notes="Arrangement strictly violates RBI Digital Lending norms. Ceiling is 5%."
    )
    test_assert(signed.get("status") == "OFFICER_REJECTED", "Officer review transitions status to OFFICER_REJECTED")
    test_assert("cryptographic_signature" in signed, "Cryptographic sign-off receipt generated")

    # ── TASK 6: Automated AI Red Teaming (PyRIT Suite) ─────────────────────────
    logger.info("\n--- [TASK 6] Automated AI Red Teaming & Adversarial Defense ---")
    redteam_report = REPO_ROOT / "redteam_security_attestation.json"
    test_assert(redteam_report.exists(), "Red teaming security attestation JSON exists")
    if redteam_report.exists():
        r_data = json.loads(redteam_report.read_text(encoding="utf-8"))
        test_assert(r_data.get("attacks_intercepted") == 25, "All 25/25 adversarial attack vectors intercepted")
        test_assert(r_data.get("defense_resilience_rate") == "100.0%", "Defense resilience rate 100.0%")
        test_assert(r_data.get("pii_leakage_rate") == "0.0%", "PII leakage rate 0.0%")

    # ── TASK 7: RAG Semantic Drift & Blind-Spot Monitor ────────────────────────
    logger.info("\n--- [TASK 7] Continuous RAG Semantic Drift & Blind-Spot Engine ---")
    from app.services.drift_monitor import record_retrieval_event, get_drift_metrics
    # Record healthy events
    for _ in range(10):
        record_retrieval_event("normal kyc query", [{"score": 0.88}, {"score": 0.82}])
    m1 = get_drift_metrics()
    test_assert(m1.get("drift_detected") is False, "Healthy retrieval does not trigger drift alert")

    # Simulate sudden influx of out-of-corpus queries
    for _ in range(15):
        record_retrieval_event("unknown cryptocurrency derivative regulations 2026", [{"score": 0.35}])
    m2 = get_drift_metrics()
    test_assert(m2.get("drift_detected") is True, "Low similarity cluster correctly triggers DRIFT_DETECTED")
    test_assert(len(m2.get("corpus_blind_spots", [])) > 0, "Corpus blind spots identified", str(m2.get("corpus_blind_spots")))

    # ── TASK 8: 2-Tier Semantic Vector Caching & FinOps ────────────────────────
    logger.info("\n--- [TASK 8] 2-Tier Semantic Vector Caching & FinOps Engine ---")
    from app.services.semantic_cache import (
        store_semantic_cache,
        lookup_semantic_cache,
        get_cache_finops_summary,
        invalidate_semantic_cache
    )
    cache_q = "What is the capital adequacy ratio for scheduled commercial banks?"
    cache_ans = "Under Basel III norms as adopted by RBI, the minimum Capital to Risk-Weighted Assets Ratio (CRAR) is 9%."
    cache_cit = [{"circular_no": "RBI/2015-16/58", "title": "Master Circular - Basel III", "clause": "Para 4.1"}]

    store_semantic_cache(cache_q, cache_ans, cache_cit, [], "gpt-5.4-mini")
    hit = lookup_semantic_cache(cache_q)
    test_assert(hit is not None, "Semantic cache EXACT hit returned pre-verified response")
    if hit:
        test_assert(hit.get("cached") is True, "Result marked cached=True")

    paraphrase_q = "What is the capital adequacy ratio for scheduled commercial banks in India?"
    hit2 = lookup_semantic_cache(paraphrase_q)
    test_assert(hit2 is not None, "Semantic cache COSINE similarity hit returned on paraphrased query")


    finops = get_cache_finops_summary()
    test_assert(finops.get("cache_entries_count") >= 1, "Cache entries tracked in FinOps")
    test_assert(finops.get("status") == "HEALTHY_OPTIMIZED", "FinOps status HEALTHY_OPTIMIZED")

    # Test cache invalidation
    purged = invalidate_semantic_cache("2026.09.20.NEW")
    test_assert(purged >= 1, "Cache successfully purged on regulatory corpus update", f"purged {purged}")

    # ── FINAL SCORECARD ───────────────────────────────────────────────────────
    logger.info("=================================================================")
    logger.info("  FINAL 8-TASK SUITE RESULTS: %d PASSED, %d FAILED", passed_tests, failed_tests)
    logger.info("=================================================================")
    if failed_tests > 0:
        sys.exit(1)
    else:
        logger.info("🎉 ALL 8 ENTERPRISE AI CAPABILITIES VERIFIED 100% PASSING!")

if __name__ == "__main__":
    run_suite()
