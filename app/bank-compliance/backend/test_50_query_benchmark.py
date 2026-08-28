"""
BankCompliance AI — 50-Query Rigorous Multi-Spectrum Benchmark Suite
=====================================================================
Evaluates:
Category A (15): Canonical In-Scope RBI & Regulatory Compliance Queries
Category B (15): Colloquial, Slang, & Semi-Correct Banking Queries
Category C (10): Gray Area & Cross-Functional Financial Queries
Category D (10): Explicit Out-of-Scope, Non-Banking, & Adversarial Queries
"""

import sys
import os
import asyncio
from pathlib import Path

# UTF-8 stdout configuration for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.services.agents.domain_guardrail import DomainCentroidGuardrail
from app.services.agents.supervisor_agent import SupervisorAgent

BENCHMARK_CASES = [
    # ── Category A: Canonical In-Scope Banking Queries (Expected: compliance_query) ──
    {"id": "A-01", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What are the acceptable officially valid documents for NRI account opening?"},
    {"id": "A-02", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "Can bank transaction data and system logs reside in a foreign cloud region?"},
    {"id": "A-03", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the mandatory cyber incident notification window to RBI and CERT-In?"},
    {"id": "A-04", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What are the restrictions on outsourcing core CISO functions?"},
    {"id": "A-05", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "Can merchants store credit card CVV or 16-digit PAN after checkout?"},
    {"id": "A-06", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the penalty for issuing an unsolicited credit card without opt-in?"},
    {"id": "A-07", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the regulatory cap on First Loss Default Guarantee (FLDG) in digital lending?"},
    {"id": "A-08", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the reporting SLA on the Central Fraud Registry for frauds over 1 lakh?"},
    {"id": "A-09", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the maximum turnaround time for internal bank grievance resolution under Ombudsman scheme?"},
    {"id": "A-10", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the minimum Common Equity Tier 1 (CET1) capital ratio under Basel III?"},
    {"id": "A-11", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the annual permissible limit under Liberalised Remittance Scheme (LRS)?"},
    {"id": "A-12", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the maximum load balance permitted on a small PPI without full KYC?"},
    {"id": "A-13", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is bank liability for loss of locker contents due to fire or theft?"},
    {"id": "A-14", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What are the four layers in Scale Based Regulation for NBFCs?"},
    {"id": "A-15", "cat": "Canonical In-Scope", "expected": "compliance_query", "query": "What is the minimum loan retention percentage required in Co-Lending Model?"},

    # ── Category B: Semi-Correct & Colloquial Banking Queries (Expected: compliance_query) ──
    {"id": "B-01", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "how to collect lending money"},
    {"id": "B-02", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "nbfc rules and regulations"},
    {"id": "B-03", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "loan recovery agent calling at 10pm is allowed?"},
    {"id": "B-04", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "bank lost my gold from locker what compensation"},
    {"id": "B-05", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "atm cut money but cash not given how many days to refund"},
    {"id": "B-06", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "can fintech company give 20% loss guarantee to bank"},
    {"id": "B-07", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "saving full aadhaar number in excel sheet legal or not"},
    {"id": "B-08", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "sending 300000 dollars abroad for university fees"},
    {"id": "B-09", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "bank credit card limit increased automatically without asking"},
    {"id": "B-10", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "hacker ransomware attack in bank server within how many hours to tell rbi"},
    {"id": "B-11", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "co-lending 80-20 rule details"},
    {"id": "B-12", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "video call kyc for customer living in dubai"},
    {"id": "B-13", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "cheque bounce multiple times red flag account timeline"},
    {"id": "B-14", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "wallet balance transfer to another bank account via upi"},
    {"id": "B-15", "cat": "Colloquial / Semi-Correct", "expected": "compliance_query", "query": "npa 90 days overdue loan classification rule"},

    # ── Category C: Gray Area / Edge Financial Queries (Expected: compliance_query) ──
    {"id": "C-01", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "dpdp act impact on customer banking database consent"},
    {"id": "C-02", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "account aggregator consent lifecycle for bank loan statement"},
    {"id": "C-03", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "green deposits framework and climate stress testing"},
    {"id": "C-04", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "priority sector lending sub-targets for small farmers"},
    {"id": "C-05", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "forensic audit mandate for red flagged corporate borrowers"},
    {"id": "C-06", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "cooling off period for personal loan borrower cancellation"},
    {"id": "C-07", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "tokenised card transaction chargeback dispute timeline"},
    {"id": "C-08", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "liquidity coverage ratio 30 day stress cash outflow formula"},
    {"id": "C-09", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "cloud exit strategy and concentration risk with single cloud provider"},
    {"id": "C-10", "cat": "Gray Area / Cross-Domain", "expected": "compliance_query", "query": "third party vendor right to audit clause mandatory in sow"},

    # ── Category D: Out-of-Scope & Adversarial Queries (Expected: out_of_scope) ──
    {"id": "D-01", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "how to fly in the sky"},
    {"id": "D-02", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "recipe for making delicious butter chicken"},
    {"id": "D-03", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "why is my bathroom running without water"},
    {"id": "D-04", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "who won the cricket world cup in 2011"},
    {"id": "D-05", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "write a python script to sort a list of numbers"},
    {"id": "D-06", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "best tourist places to visit in Goa during winter"},
    {"id": "D-07", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "how to repair a flat bicycle tyre"},
    {"id": "D-08", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "tell me a funny bedtime joke for kids"},
    {"id": "D-09", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "what is the capital of France"},
    {"id": "D-10", "cat": "Out-of-Scope", "expected": "out_of_scope", "query": "how to install windows 11 on an old laptop"}
]

async def run_50_query_benchmark():
    DomainCentroidGuardrail.initialize()
    
    print("=" * 80)
    print(" 🧪 RUNNING 50-QUERY COMPLIANCE & GUARDRAIL SPECTRUM BENCHMARK")
    print("=" * 80)
    
    passed_count = 0
    failures = []
    
    for case in BENCHMARK_CASES:
        state = {
            "sanitized_query": case["query"],
            "history": []
        }
        
        # Execute Supervisor planning step
        res_state = await SupervisorAgent.plan(state)
        actual_intent = res_state.get("intent")
        
        # Evaluate mathematical scores
        is_in_domain, c_sim, m_sim = DomainCentroidGuardrail.evaluate(case["query"])
        
        is_correct = (actual_intent == case["expected"])
        if is_correct:
            passed_count += 1
            status_icon = "✅"
        else:
            status_icon = "❌"
            failures.append({
                "id": case["id"],
                "query": case["query"],
                "cat": case["cat"],
                "expected": case["expected"],
                "actual": actual_intent,
                "centroid_sim": c_sim,
                "max_clause_sim": m_sim
            })
            
        print(f"{status_icon} [{case['id']}] {case['cat'][:14]:14} | Expected: {case['expected'][:12]:12} | Actual: {actual_intent[:12]:12} | Sim: C={c_sim:.3f}, M={m_sim:.3f} | \"{case['query'][:40]}...\"")

    print("\n" + "=" * 80)
    accuracy = (passed_count / len(BENCHMARK_CASES)) * 100
    print(f" 📊 BENCHMARK SUMMARY: {passed_count}/{len(BENCHMARK_CASES)} Passed ({accuracy:.1f}% Accuracy)")
    print("=" * 80)
    
    if failures:
        print(f"\n⚠️ {len(failures)} Failure Cases Identified:")
        for f in failures:
            print(f"  • [{f['id']}] \"{f['query']}\"")
            print(f"    Expected: {f['expected']} ➔ Actual: {f['actual']} (C_Sim: {f['centroid_sim']:.4f}, M_Sim: {f['max_clause_sim']:.4f})")
    else:
        print("\n🎉 PERFECT SCORE: 100% of 50 multi-spectrum queries classified flawlessly!")

if __name__ == "__main__":
    asyncio.run(run_50_query_benchmark())
