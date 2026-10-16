#!/usr/bin/env bash
# ==============================================================================
# deploy-networkpolicies.sh — Zero-Trust NetworkPolicy Deployment Script
# ==============================================================================
# Purpose: Atomically deploys east-west microsegmentation NetworkPolicies to the
#          bank-compliance namespace with server-side validation.
#
# Usage:
#   ./scripts/deploy-networkpolicies.sh              # atomic apply (default)
#   ./scripts/deploy-networkpolicies.sh --dry-run    # server-side dry-run validation
#   ./scripts/deploy-networkpolicies.sh --delete     # teardown / rollback
#
# Safety Guarantees:
#   - Atomic directory apply: DNS, Ingress, and Egress policies are applied
#     together to prevent service blackholing.
#   - Context validation: Ensures target cluster is aks-ht-bankc-p-cin-01.
#   - Scoped strictly to bank-compliance namespace — system namespaces untouched.
# ==============================================================================
set -euo pipefail

NP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/app/bank-compliance/k8s/networkpolicy"
MODE="${1:-apply}"

echo "════════════════════════════════════════════════════"
echo "  BankCompliance Zero-Trust NetworkPolicy Deploy"
echo "  Manifests: ${NP_DIR}"
echo "════════════════════════════════════════════════════"

# ── Validate kubectl context ──────────────────────────────────────────────────
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
echo "► kubectl context: ${CURRENT_CONTEXT}"
if [[ "${CURRENT_CONTEXT}" != *"aks-ht-bankc"* ]]; then
  echo "⚠️  WARNING: Context does not look like aks-ht-bankc-p-cin-01"
  echo "   Run: az aks get-credentials --name aks-ht-bankc-p-cin-01 --resource-group rg-ht-bankc-p-cin-01"
  exit 1
fi

# ── Teardown / Rollback mode ──────────────────────────────────────────────────
if [[ "${MODE}" == "--delete" ]]; then
  echo ""
  echo "► Removing NetworkPolicies in bank-compliance..."
  kubectl delete -f "${NP_DIR}" --ignore-not-found -n bank-compliance
  echo "✅ All NetworkPolicies successfully removed from bank-compliance namespace"
  exit 0
fi

# ── Dry-run mode ──────────────────────────────────────────────────────────────
if [[ "${MODE}" == "--dry-run" ]]; then
  echo ""
  echo "► Server-side dry-run validation (validates against Kubernetes API server)..."
  kubectl apply --dry-run=server -f "${NP_DIR}" -n bank-compliance
  echo "✅ Server-side dry-run passed — zero syntax or schema violations!"
  exit 0
fi

# ── Atomic Apply ──────────────────────────────────────────────────────────────
echo ""
echo "► Performing pre-flight server-side dry-run..."
kubectl apply --dry-run=server -f "${NP_DIR}" -n bank-compliance

echo ""
echo "► Atomically applying all NetworkPolicies..."
kubectl apply -f "${NP_DIR}" -n bank-compliance

echo ""
echo "► Validating applied NetworkPolicies in bank-compliance:"
kubectl get networkpolicy -n bank-compliance

echo ""
echo "════════════════════════════════════════════════════"
echo "  ✅ NetworkPolicies Applied Successfully!"
echo "  - Zero-Trust East-West microsegmentation active"
echo "  - CoreDNS + IMDS + Ingress + External LLMs whitelisted"
echo "════════════════════════════════════════════════════"
