#!/usr/bin/env bash
# ==============================================================================
# deploy-gatekeeper.sh — Reproducible OPA Gatekeeper ConstraintTemplate Deploy
# ==============================================================================
# Usage:
#   ./scripts/deploy-gatekeeper.sh              # apply (default)
#   ./scripts/deploy-gatekeeper.sh --dry-run    # server-side dry-run (safe check)
#   ./scripts/deploy-gatekeeper.sh --delete     # remove all constraints + templates
#
# Prerequisites:
#   - kubectl configured against aks-ht-bankc-p-cin-01
#   - AKS cluster running (az aks start if stopped)
#   - azure_policy_enabled = true on AKS (Gatekeeper webhook already live)
#
# Safety:
#   - enforcementAction: warn in all constraints — NEVER blocks pods
#   - Scoped to bank-compliance namespace only — kube-system untouched
# ==============================================================================
set -euo pipefail

GATEKEEPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/app/bank-compliance/k8s/gatekeeper"
DRY_RUN="${1:-}"

echo "════════════════════════════════════════════════════"
echo "  OPA Gatekeeper ConstraintTemplate Deploy"
echo "  Dir: ${GATEKEEPER_DIR}"
echo "════════════════════════════════════════════════════"

# ── Validate kubectl context ──────────────────────────────────────────────────
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
echo "► kubectl context: ${CURRENT_CONTEXT}"
if [[ "${CURRENT_CONTEXT}" != *"aks-ht-bankc"* ]]; then
  echo "⚠️  WARNING: Context does not look like aks-ht-bankc-p-cin-01"
  echo "   Run: az aks get-credentials --name aks-ht-bankc-p-cin-01 --resource-group rg-ht-bankc-p-cin-01"
  exit 1
fi

# ── Delete mode ───────────────────────────────────────────────────────────────
if [[ "${DRY_RUN}" == "--delete" ]]; then
  echo ""
  echo "► Removing Constraints (must delete before ConstraintTemplates)"
  kubectl delete -f "${GATEKEEPER_DIR}/constraint-nonroot-bankc.yaml" --ignore-not-found
  kubectl delete -f "${GATEKEEPER_DIR}/constraint-registries-bankc.yaml" --ignore-not-found
  echo "► Removing ConstraintTemplates"
  kubectl delete -f "${GATEKEEPER_DIR}/ct-require-nonroot.yaml" --ignore-not-found
  kubectl delete -f "${GATEKEEPER_DIR}/ct-allowed-registries.yaml" --ignore-not-found
  echo "✅ Gatekeeper policies removed"
  exit 0
fi

# ── Dry-run mode ──────────────────────────────────────────────────────────────
if [[ "${DRY_RUN}" == "--dry-run" ]]; then
  echo ""
  echo "► Server-side dry-run (validates against live API server — no resources created)"
  kubectl apply --dry-run=server -f "${GATEKEEPER_DIR}/ct-require-nonroot.yaml"
  kubectl apply --dry-run=server -f "${GATEKEEPER_DIR}/ct-allowed-registries.yaml"
  kubectl apply --dry-run=server -f "${GATEKEEPER_DIR}/constraint-nonroot-bankc.yaml"
  kubectl apply --dry-run=server -f "${GATEKEEPER_DIR}/constraint-registries-bankc.yaml"
  echo "✅ Dry-run passed — safe to apply"
  exit 0
fi

# ── Apply mode ────────────────────────────────────────────────────────────────
echo ""
echo "► Step 1/4 — Apply ConstraintTemplate: K8sRequireNonRoot"
kubectl apply -f "${GATEKEEPER_DIR}/ct-require-nonroot.yaml"

echo "► Step 2/4 — Apply ConstraintTemplate: K8sAllowedRegistries"
kubectl apply -f "${GATEKEEPER_DIR}/ct-allowed-registries.yaml"

echo ""
echo "► Waiting 15s for CRDs to register in API server..."
sleep 15

echo ""
echo "► Step 3/4 — Apply Constraint: require-nonroot-bank-compliance (warn)"
kubectl apply -f "${GATEKEEPER_DIR}/constraint-nonroot-bankc.yaml"

echo "► Step 4/4 — Apply Constraint: allowed-registries-bank-compliance (warn)"
kubectl apply -f "${GATEKEEPER_DIR}/constraint-registries-bankc.yaml"

echo ""
echo "════════════════════════════════════════════════════"
echo "✅ Gatekeeper policies applied (enforcementAction: warn)"
echo "════════════════════════════════════════════════════"
echo ""
echo "► Verify ConstraintTemplates:"
kubectl get constrainttemplates k8srequirenonroot k8sallowedregistries
echo ""
echo "► Check for violations (should be 0 — existing pods are already compliant):"
kubectl describe k8srequirenonroot require-nonroot-bank-compliance 2>/dev/null | grep -A5 "Violations:" || true
kubectl describe k8sallowedregistries allowed-registries-bank-compliance 2>/dev/null | grep -A5 "Violations:" || true
echo ""
echo "► To harden to deny mode after confirming 0 violations:"
echo "   Edit constraint files: enforcementAction: warn → deny"
echo "   Re-run: ./scripts/deploy-gatekeeper.sh"
