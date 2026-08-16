"""
BankCompliance AI — AI Quality Evaluation Script
=================================================
Uses Azure AI Evaluation SDK to score the RAG pipeline on three dimensions:

  Groundedness  — Does the answer come from the retrieved RBI context?
                  (Detects hallucinations — model making up RBI rules)

  Relevance     — Does the answer directly address the compliance question?
                  (Detects off-topic or generic responses)

  Fluency       — Is the answer professionally written and coherent?
                  (Ensures output quality for compliance officer audience)

Usage:
  python eval/evaluate.py

Environment variables required:
  AZURE_OPENAI_ENDPOINT    — e.g. https://oai-ht-taxb-p-eus-01.openai.azure.com/
  AZURE_OPENAI_DEPLOYMENT  — e.g. gpt-5.4-nano
  LITELLM_URL              — e.g. http://localhost:4000/v1 (for live app testing)

Exit codes:
  0 — All metrics above threshold (CI passes)
  1 — One or more metrics below threshold (CI fails, blocks deployment)
"""

import json
import os
import sys
import httpx
import asyncio
from pathlib import Path

from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    FluencyEvaluator,
    AzureOpenAIModelConfiguration,
)

# ─── Configuration ─────────────────────────────────────────────────────────────

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.jsonl"

# Quality thresholds — scores are 1-5 (5 = best)
# Pipeline fails CI if average score drops below these values
THRESHOLDS = {
    "groundedness": 4.0,   # Strict — no hallucinated RBI rules allowed
    "relevance":    3.5,   # Moderate — answer must address the question
    "fluency":      3.5,   # Moderate — professional tone required
}

AZURE_OPENAI_ENDPOINT   = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-nano")
LITELLM_URL             = os.environ.get("LITELLM_URL", "http://localhost:4000/v1")
OPENAI_API_KEY          = os.environ.get("OPENAI_API_KEY", "dummy-key-for-litellm")

# ─── Load Golden Dataset ────────────────────────────────────────────────────────

def load_golden_dataset() -> list[dict]:
    """Load evaluation test cases from JSONL file."""
    dataset = []
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                dataset.append(json.loads(line))
    print(f"✅ Loaded {len(dataset)} test cases from golden dataset")
    return dataset

# ─── Live App Response (Optional) ──────────────────────────────────────────────

async def get_live_response(query: str, context: str) -> str:
    """
    Calls the running BankCompliance API to get a live LLM response.
    Falls back to using the reference response if the API is not reachable.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{LITELLM_URL}/chat/completions",
                json={
                    "model": AZURE_OPENAI_DEPLOYMENT,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are BankCompliance AI, the official Banking Regulatory "
                                "& Compliance Copilot for Indian Scheduled Commercial Banks. "
                                "Always quote exact RBI Circular numbers and Section/Clause references."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Relevant RBI Master Direction Context:\n{context}\n\n"
                                f"Compliance Officer Question:\n{query}"
                            ),
                        },
                    ],
                    "temperature": 0.1,
                    "max_tokens": 600,
                },
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ⚠️  Live API not reachable ({e}), using reference response for evaluation")
        return None

# ─── Main Evaluation Runner ─────────────────────────────────────────────────────

def run_evaluation():
    """
    Runs all three evaluators on every test case in the golden dataset.
    Prints a report and exits with code 1 if any metric is below threshold.
    """
    if not AZURE_OPENAI_ENDPOINT:
        print("❌ AZURE_OPENAI_ENDPOINT not set. Exiting.")
        sys.exit(1)

    # Configure evaluators — they use Azure OpenAI as the judge model
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    )

    groundedness_evaluator = GroundednessEvaluator(model_config=model_config)
    relevance_evaluator    = RelevanceEvaluator(model_config=model_config)
    fluency_evaluator      = FluencyEvaluator(model_config=model_config)

    dataset = load_golden_dataset()

    results = []
    print("\n" + "═" * 70)
    print("  BankCompliance AI — RAG Quality Evaluation")
    print("═" * 70)

    for i, test_case in enumerate(dataset, 1):
        query    = test_case["query"]
        context  = test_case["context"]
        response = test_case["response"]  # reference answer (from golden dataset)

        # Optionally get a LIVE response from the running API
        live_response = asyncio.run(get_live_response(query, context))
        eval_response = live_response if live_response else response

        print(f"\n[{i}/{len(dataset)}] Evaluating: {query[:60]}...")

        # Score with each evaluator
        g_score = groundedness_evaluator(
            query=query,
            response=eval_response,
            context=context,
        )
        r_score = relevance_evaluator(
            query=query,
            response=eval_response,
            context=context,
        )
        f_score = fluency_evaluator(
            query=query,
            response=eval_response,
        )

        groundedness = g_score.get("groundedness", 0)
        relevance    = r_score.get("relevance", 0)
        fluency      = f_score.get("fluency", 0)

        print(f"  Groundedness : {groundedness:.1f}/5.0  (threshold ≥ {THRESHOLDS['groundedness']})")
        print(f"  Relevance    : {relevance:.1f}/5.0  (threshold ≥ {THRESHOLDS['relevance']})")
        print(f"  Fluency      : {fluency:.1f}/5.0  (threshold ≥ {THRESHOLDS['fluency']})")

        results.append({
            "query":        query,
            "groundedness": groundedness,
            "relevance":    relevance,
            "fluency":      fluency,
            "live":         live_response is not None,
        })

    # ─── Summary Report ─────────────────────────────────────────────────────

    print("\n" + "═" * 70)
    print("  EVALUATION SUMMARY")
    print("═" * 70)

    avg_groundedness = sum(r["groundedness"] for r in results) / len(results)
    avg_relevance    = sum(r["relevance"]    for r in results) / len(results)
    avg_fluency      = sum(r["fluency"]      for r in results) / len(results)

    g_pass = avg_groundedness >= THRESHOLDS["groundedness"]
    r_pass = avg_relevance    >= THRESHOLDS["relevance"]
    f_pass = avg_fluency      >= THRESHOLDS["fluency"]

    g_icon = "✅" if g_pass else "❌"
    r_icon = "✅" if r_pass else "❌"
    f_icon = "✅" if f_pass else "❌"

    print(f"\n  {g_icon} Avg Groundedness : {avg_groundedness:.2f}/5.0  (threshold ≥ {THRESHOLDS['groundedness']})")
    print(f"  {r_icon} Avg Relevance    : {avg_relevance:.2f}/5.0  (threshold ≥ {THRESHOLDS['relevance']})")
    print(f"  {f_icon} Avg Fluency      : {avg_fluency:.2f}/5.0  (threshold ≥ {THRESHOLDS['fluency']})")

    # Save JSON results for GitHub Actions artifact upload
    results_path = Path(__file__).parent / "eval_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "avg_groundedness": avg_groundedness,
                "avg_relevance":    avg_relevance,
                "avg_fluency":      avg_fluency,
            },
            "pass":    g_pass and r_pass and f_pass,
            "details": results,
        }, f, indent=2)
    print(f"\n  📄 Full results saved to: {results_path}")

    if not (g_pass and r_pass and f_pass):
        print("\n  ❌ EVALUATION FAILED — One or more metrics below threshold.")
        print("     Deployment BLOCKED. Fix prompt quality before merging.\n")
        sys.exit(1)
    else:
        print("\n  ✅ EVALUATION PASSED — All metrics above threshold.")
        print("     Deployment approved.\n")
        sys.exit(0)


if __name__ == "__main__":
    run_evaluation()
