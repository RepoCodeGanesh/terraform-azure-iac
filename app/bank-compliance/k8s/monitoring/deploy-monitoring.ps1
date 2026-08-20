<#
.SYNOPSIS
    Deploys Prometheus and Grafana (kube-prometheus-stack) to AKS and applies ServiceMonitors.
.DESCRIPTION
    Automates Helm repository setup, namespace creation, installation/upgrade, and ServiceMonitor configuration.
#>

param (
    [string]$Namespace = "monitoring",
    [string]$ReleaseName = "monitoring",
    [string]$ValuesFile = "$PSScriptRoot\values.yaml"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  AKS Observability Deployment: Prometheus + Grafana      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Add & Update Helm Repo
Write-Host "`n[1/4] Adding/Updating Prometheus Community Helm repository..." -ForegroundColor Yellow
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 2. Deploy kube-prometheus-stack
Write-Host "`n[2/4] Deploying kube-prometheus-stack to namespace '$Namespace'..." -ForegroundColor Yellow
helm upgrade --install $ReleaseName prometheus-community/kube-prometheus-stack `
  --namespace $Namespace `
  --create-namespace `
  --values $ValuesFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install kube-prometheus-stack."
    exit $LASTEXITCODE
}

# 3. Apply ServiceMonitors and Pre-built Dashboards
Write-Host "`n[3/4] Applying ServiceMonitors and Dashboards in '$Namespace' & 'bank-compliance'..." -ForegroundColor Yellow
kubectl apply -f "$PSScriptRoot\service-monitors.yaml"
kubectl apply -f "$PSScriptRoot\bank-compliance-dashboard.yaml"

# 4. Success Summary & Instructions
Write-Host "`n[4/4] Observability Stack Successfully Deployed!" -ForegroundColor Green
Write-Host "----------------------------------------------------------" -ForegroundColor Gray
Write-Host "Access Grafana (Dashboard UI):" -ForegroundColor Cyan
Write-Host "  kubectl port-forward svc/$ReleaseName-grafana 3000:80 -n $Namespace"
Write-Host "  URL: http://localhost:3000"
Write-Host "  User: admin"
Write-Host "  Pass: AdminSecurePassword123!"
Write-Host "----------------------------------------------------------" -ForegroundColor Gray
Write-Host "Access Prometheus (Query & Targets UI):" -ForegroundColor Cyan
Write-Host "  kubectl port-forward svc/$ReleaseName-kube-prometheus-prometheus 9090:9090 -n $Namespace"
Write-Host "  URL: http://localhost:9090"
Write-Host "==========================================================" -ForegroundColor Cyan
