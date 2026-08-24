"""
Generate Real-Time Executive Drift Governance Dashboard
======================================================
Aggregates individual status JSON artifacts from all 5 CAF infrastructure roots
and appends a clean, formatted Markdown dashboard to $GITHUB_STEP_SUMMARY.
"""

from pathlib import Path
import json
import glob
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    search_dir = sys.argv[1] if len(sys.argv) > 1 else "all-statuses"
    
    files = glob.glob(f"{search_dir}/**/status-*.json", recursive=True) + glob.glob(f"{search_dir}/status-*.json")
    raw_results = []
    
    for f in set(files):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                raw_results.append(json.load(fp))
        except Exception as e:
            print(f"[WARN] Failed to read {f}: {e}")

    # Deduplicate strictly by target root path
    results_map = {r["root"]: r for r in raw_results if "root" in r}
    results = list(results_map.values())

    has_drift = any(r.get("status") == "DRIFTED" for r in results)
    has_error = any(r.get("status") == "ERROR" for r in results)

    if has_error:
        overall_status = "🔴 ATTENTION REQUIRED (EXECUTION ERRORS DETECTED)"
    elif has_drift:
        overall_status = "🟡 DRIFT DETECTED (RECONCILIATION REQUIRED)"
    elif len(results) > 0:
        overall_status = "🟢 100% IN SYNC (ZERO DRIFT)"
    else:
        overall_status = "⚪ NO STATUSES RECORDED"

    notification_email = os.environ.get("NOTIFICATION_EMAIL", "richtextforganesh@outlook.com")

    md = []
    md.append("# 🛡️ Enterprise Terraform Drift Governance Report")
    md.append("")
    md.append(f"> **Overall Platform Health:** `{overall_status}` | **Scanned Roots:** `{len(results)} CAF Roots`")
    md.append(f"> **Tenant ID:** `4cef0d84-84d6-4ed0-8abe-773b015bcf99` | **Alert Notification:** `{notification_email}`")
    md.append("")
    md.append("---")
    md.append("")
    md.append("### 📋 Real-Time Infrastructure Status Matrix")
    md.append("")
    md.append("| Infrastructure Scope | Terraform State Root | Subscription ID | Live Governance Status |")
    md.append("|---|---|---|:---:|")

    for r in sorted(results, key=lambda x: x.get("root", "")):
        name = r.get("name", "Unknown Scope")
        root = r.get("root", "Unknown Root")
        sub_id = r.get("sub_id", "Unknown Sub")
        badge = r.get("badge", "UNKNOWN")
        md.append(f"| **{name}** | `{root}` | `{sub_id}` | {badge} |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("### 🛠️ Self-Healing & Drift Reconciliation Runbook:")
    md.append("* **If Status is 🟢 IN SYNC:** Zero action required. Live cloud resources match committed Git IaC.")
    md.append("* **If Status is 🟡 DRIFT DETECTED:**")
    md.append("  1. An automated GitHub Issue has been opened with the full `terraform plan` delta diff.")
    md.append("  2. **Unintended Drift:** Trigger the corresponding workload IaC workflow to apply and self-heal.")
    md.append("  3. **Intended Drift (Hotfix):** Update your Terraform `.tf` files in `main` to match live Azure state.")
    md.append("* **If Status is 🔴 EXECUTION ERROR:** Review authentication or variable configuration in the failed stage.")

    summary_content = "\n".join(md) + "\n"

    # Write to GitHub Step Summary if running in Actions, else stdout
    step_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary_path:
        with open(step_summary_path, "a", encoding="utf-8") as s:
            s.write(summary_content)
        print("[SUCCESS] Appended executive dashboard to GITHUB_STEP_SUMMARY")
    else:
        print(summary_content)

if __name__ == "__main__":
    main()
