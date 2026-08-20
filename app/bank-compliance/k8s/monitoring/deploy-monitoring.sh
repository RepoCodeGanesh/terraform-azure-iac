#!/usr/bin/env bash
# ==============================================================================
# Deploys Prometheus and Grafana (kube-prometheus-stack) to AKS
# ==============================================================================
set -e

NAMESPACE="${1:-monitoring}"
RELEASE_NAME="${2:-monitoring}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALUES_FILE="$DIR/values.yaml"

echo "=========================================================="
echo "  AKS Observability Deployment: Prometheus + Grafana      "
echo "=========================================================="

echo -e "\n[1/4] Adding/Updating Prometheus Community Helm repository..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo -e "\n[2/4] Deploying kube-prometheus-stack to namespace '$NAMESPACE'..."
helm upgrade --install "$RELEASE_NAME" prometheus-community/kube-prometheus-stack \
  --namespace "$NAMESPACE" \
  --create-namespace \
  --values "$VALUES_FILE"

# 3. Apply ServiceMonitors and Pre-built Dashboards
echo -e "\n[3/4] Applying ServiceMonitors and Dashboards in '$NAMESPACE' & 'bank-compliance'..."
kubectl apply -f "$DIR/service-monitors.yaml"
kubectl apply -f "$DIR/bank-compliance-dashboard.yaml"

echo -e "\n[4/4] Observability Stack Successfully Deployed!"
echo "----------------------------------------------------------"
echo "Access Grafana (Dashboard UI):"
echo "  kubectl port-forward svc/$RELEASE_NAME-grafana 3000:80 -n $NAMESPACE"
echo "  URL: http://localhost:3000"
echo "  User: admin | Pass: AdminSecurePassword123!"
echo "----------------------------------------------------------"
echo "Access Prometheus (Query UI):"
echo "  kubectl port-forward svc/$RELEASE_NAME-kube-prometheus-prometheus 9090:9090 -n $NAMESPACE"
echo "  URL: http://localhost:9090"
echo "=========================================================="
