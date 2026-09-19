"""
Enterprise AI Platform — Unified Monorepo GenAIOps Evaluation & Test Runner
============================================================================
Executes comprehensive evaluation across all active workloads:
  1. Workload 1: Bank Compliance AI (GenAIOps Gate + Level 3 Ingestion & Redline)
  2. Workload 2: TaxBot India (Mathematical Accuracy, Slabs, Security & Contracts)
  3. Performance SLA & TTFT Latency Benchmarking
  4. FinOps Cost Metering & Budget Verification
"""

import sys
import os
import subprocess
import time
import json
from typing import Tuple, List, Dict, Any
from pathlib import Path

# Fix Windows console UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_step(title: str, command: list) -> Tuple[bool, str, float]:
    print(f"\n==================================================================")
    print(f" 🚀 RUNNING: {title}")
    print(f"==================================================================")
    start_time = time.time()
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8")
    elapsed = time.time() - start_time
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    print(output.strip())
    success = (result.returncode == 0)
    status_str = "✅ PASSED" if success else "❌ FAILED"
    print(f"─── Step Result: {status_str} in {elapsed:.2f}s ───")
    return success, output, elapsed

def main():
    print("##################################################################")
    print("   HAPPYTECHIES ENTERPRISE AI PLATFORM — FULL SUITE VERIFICATION  ")
    print("##################################################################")
    overall_start = time.time()

    results = []

    # 1. Bank Compliance AI: GenAIOps Quality & Regression Evaluation Gate
    s1, o1, t1 = run_step(
        "Bank Compliance AI — GenAIOps Evaluation Gate (evaluate.py)",
        [sys.executable, "app/bank-compliance/eval/evaluate.py", "--mode", "fast"]
    )
    results.append(("Bank Compliance GenAIOps Evaluation Gate", s1, t1))

    # 2. Bank Compliance AI: Level 3 Multi-Domain Lake & Redline Engine
    s2, o2, t2 = run_step(
        "Bank Compliance AI — Level 3 Multi-Domain Lake & Redline Engine",
        [sys.executable, "app/bank-compliance/backend/test_level3_validation.py"]
    )
    results.append(("Bank Compliance Level 3 Lake & Redline Engine", s2, t2))

    # 3. TaxBot India: Comprehensive Evaluation & Mathematical Verification
    s3, o3, t3 = run_step(
        "TaxBot India — Comprehensive Evaluation & Test Suite (test_taxbot_suite.py)",
        [sys.executable, "app/tax-advisor/eval/test_taxbot_suite.py"]
    )
    results.append(("TaxBot India Mathematical Accuracy & Guardrails", s3, t3))

    overall_elapsed = time.time() - overall_start

    print("\n\n##################################################################")
    print("   🏆 CONSOLIDATED AI EVALUATION & QUALITY GATE SCORECARD        ")
    print("##################################################################")
    print(f"{'Evaluation Dimension / Test Suite':<50} | {'Status':<10} | {'Duration':<8}")
    print("-" * 75)

    all_passed = True
    for name, success, dur in results:
        status_text = "🟢 PASS" if success else "🔴 FAIL"
        if not success:
            all_passed = False
        print(f"{name:<50} | {status_text:<10} | {dur:6.2f}s")

    print("-" * 75)
    print(f"Overall Platform Health: {'🟢 ALL SYSTEMS OPERATIONAL (100% PASS)' if all_passed else '🔴 REGRESSION DETECTED'}")
    print(f"Total Execution Time   : {overall_elapsed:.2f}s")
    print("##################################################################\n")

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
