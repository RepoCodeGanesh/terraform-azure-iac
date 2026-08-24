# Comprehensive Guide: AKS Hybrid Observability (Azure Container Insights + Prometheus & Grafana)

## 1. Architecture Overview

This enterprise repository implements the **Hybrid Observability Pattern** for Azure Kubernetes Service (`aks-ht-bankc-p-cin-01`). Instead of choosing between Azure-native tools or open-source tooling, we leverage **both** for their distinct strengths at **near-zero cost**:

```mermaid
flowchart TD
    subgraph AKS ["Azure Kubernetes Service (aks-ht-bankc-p-cin-01)"]
        subgraph AppNamespace ["Namespace: bank-compliance"]
            FastAPI["FastAPI Backend<br/>(:8000/metrics)"]
            LiteLLM["LiteLLM Proxy<br/>(:4000/metrics)"]
            Qdrant["Qdrant Vector DB<br/>(:6333)"]
        end

        subgraph MonitoringNamespace ["Namespace: monitoring"]
            Prom["Prometheus Server (TSDB)"]
            Graf["Grafana Dashboards"]
            SM["ServiceMonitors / Exporters"]
        end

        AMA["Azure Monitor Agent (DaemonSet)"]
    end

    subgraph AzureShared ["Shared Services Subscription"]
        LAW["Log Analytics Workspace<br/>(law-ht-ss-p-cin-01)"]
        AppInsights["Application Insights<br/>(appi-ht-bankc-p-cin-01)"]
        Portal["Azure Portal<br/>(Insights & Workbooks)"]
    end

    %% Data Flows
    FastAPI -- "stdout/stderr logs" --> AMA
    LiteLLM -- "stdout/stderr logs" --> AMA
    AMA --> LAW --> Portal

    FastAPI -- "HTTP /metrics" --> Prom
    LiteLLM -- "HTTP /metrics" --> Prom
    SM --> Prom
    Prom --> Graf
    Graf --> Engineers["Engineers / DevOps / SREs"]
```

---

## 2. Division of Responsibilities

| Observability Pillar | Option 1: Azure Container Insights (Native) | Option 2: Prometheus + Grafana (Self-Hosted) |
| :--- | :--- | :--- |
| **Primary Focus** | Centralized Logs, Platform Audit, Azure Security | Real-time Metrics, Custom AI/LLM Dashboards |
| **Data Ingestion** | Pod `stdout`/`stderr`, K8s events, Node OS logs | Numerical time-series metrics via HTTP `/metrics` |
| **Query Language** | **KQL** (Kusto Query Language) | **PromQL** (Prometheus Query Language) |
| **Visualization** | Azure Portal (Insights tab, Azure Workbooks) | Grafana Web Dashboards (`http://localhost:3000`) |
| **Alerting** | Azure Monitor Action Groups (Email/SMS/Webhooks) | Alertmanager (Slack/PagerDuty/Webhooks) |
| **Cost** | **$0 extra** (within 5 GB/month free Log Analytics tier) | **$0 software license** (runs on existing worker nodes) |

---

## 3. Option 1: Azure Container Insights Setup & KQL Queries

### A. Terraform Configuration
Container Insights is enabled via the `oms_agent` block in [`modules/aks/main.tf`](file:///c:/Users/RichT/OneDrive/Documents/Repos/terraform-azure-iac/modules/aks/main.tf) and called by [`workloads/bank-compliance-ai-aks/aks_cluster.tf`](file:///c:/Users/RichT/OneDrive/Documents/Repos/terraform-azure-iac/workloads/bank-compliance-ai-aks/aks_cluster.tf):

```hcl
# In modules/aks/main.tf:
resource "azurerm_kubernetes_cluster" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  # ...
  dynamic "oms_agent" {
    for_each = var.log_analytics_workspace_id != null ? [1] : []
    content {
      log_analytics_workspace_id      = var.log_analytics_workspace_id
      msi_auth_for_monitoring_enabled = true
    }
  }
}

resource "azurerm_monitor_diagnostic_setting" "aks_diagnostics" {
  count                      = var.log_analytics_workspace_id != null ? 1 : 0
  name                       = "diag-${var.name}"
  target_resource_id         = azurerm_kubernetes_cluster.this.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log { category = "kube-apiserver" }
  enabled_log { category = "kube-audit-admin" }
  enabled_log { category = "kube-controller-manager" }
  enabled_log { category = "cluster-autoscaler" }
  enabled_metric { category = "AllMetrics" }
}
```

### B. Viewing in Azure Portal
1. Navigate to **Azure Portal** ➔ **Kubernetes services** ➔ `aks-ht-bankc-p-cin-01`.
2. Select **Insights** under the *Monitoring* section.
3. Access tabs:
   * **Cluster:** Overview of node CPU and memory utilization.
   * **Nodes:** Health status of the VM scale set instances.
   * **Controllers:** Real-time container restarts and pod execution status.
   * **Containers:** Detailed logs and status per container.

### C. Curated KQL Queries (Log Analytics)

Run these queries in **Log Analytics Workspace** (`law-ht-ss-p-cin-01`):

#### 1. Find Application Errors & Exceptions (500s / Exceptions):
```kql
ContainerLogV2
| where TimeGenerated > ago(1h)
| where PodNamespace == "bank-compliance"
| where LogMessage has "error" or LogMessage has "exception" or LogMessage has "500"
| project TimeGenerated, PodName, ContainerName, LogMessage
| order by TimeGenerated desc
```

#### 2. Detect OOMKilled or Crashing Pods:
```kql
KubePodInventory
| where TimeGenerated > ago(24h)
| where Namespace == "bank-compliance"
| where PodStatus in ("Failed", "CrashLoopBackOff", "Terminating") or ContainerStatusReason == "OOMKilled"
| summarize RestartCount = max(ContainerRestartCount) by PodName = Name, ContainerStatusReason, bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

#### 3. Pod CPU & Memory Consumption Breakdown:
```kql
Perf
| where TimeGenerated > ago(1h)
| where ObjectName == "K8SContainer"
| where CounterName in ("cpuUsageNanoCores", "memoryWorkingSetBytes")
| summarize AvgValue = avg(CounterValue) by InstanceName, CounterName, bin(TimeGenerated, 5m)
| render timechart
```

---

## 4. Option 2: Self-Hosted Prometheus + Grafana Setup & Dashboard Access

### A. Quick Deployment (1-Click)

The repository provides automated deployment scripts in [`app/bank-compliance/k8s/monitoring/`](file:///c:/Users/RichT/OneDrive/Documents/Repos/terraform-azure-iac/app/bank-compliance/k8s/monitoring/):

#### On Windows (PowerShell):
```powershell
# Authenticate with AKS
az aks get-credentials --resource-group rg-ht-bankc-p-cin-01 --name aks-ht-bankc-p-cin-01

# Run deployment script
.\app\bank-compliance\k8s\monitoring\deploy-monitoring.ps1
```

#### On Linux / macOS / Bash:
```bash
az aks get-credentials --resource-group rg-ht-bankc-p-cin-01 --name aks-ht-bankc-p-cin-01
chmod +x app/bank-compliance/k8s/monitoring/deploy-monitoring.sh
./app/bank-compliance/k8s/monitoring/deploy-monitoring.sh
```

---

### B. Opening and Viewing Dashboards

#### 1. Open Grafana:
```powershell
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```
* **URL:** `http://localhost:3000`
* **Username:** `admin`
* **Password:** `AdminSecurePassword123!` *(configured in values.yaml)*

#### 2. Open Prometheus Query & Targets UI:
```powershell
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring
```
* **URL:** `http://localhost:9090`
* Check scraped endpoints: Go to **Status** ➔ **Targets**.

---

### C. Built-in Grafana Dashboards Included

Once inside Grafana, click **Dashboards** ➔ **Browse** to open pre-loaded dashboards:

| Dashboard Name | Purpose | Key Metrics |
| :--- | :--- | :--- |
| **🏦 BankCompliance AI Workload Dashboard** | **Dedicated AI & App Dashboard** | LiteLLM request rates, p95 LLM latency, Token consumption, FastAPI throughput & 5xx error rate, Pod RAM/CPU |
| **Kubernetes / Compute Resources / Cluster** | Cluster-wide utilization | Total CPU/RAM committed vs capacity |
| **Kubernetes / Compute Resources / Namespace (Pods)** | Resource consumption per namespace | Pod CPU limits, memory working sets, network I/O |
| **Kubernetes / Compute Resources / Pod** | Single pod drill-down | Container restarts, throttling, memory RSS |
| **Node Exporter / Use Method / Node** | VM hardware health | Disk IOPS, filesystem storage usage, OS load |

---

## 5. Custom AI / LLM Observability with PromQL

The AI app pods ([`bankc-backend`](file:///c:/Users/RichT/OneDrive/Documents/Repos/terraform-azure-iac/app/bank-compliance/k8s/backend-deployment.yaml) and [`litellm-proxy`](file:///c:/Users/RichT/OneDrive/Documents/Repos/terraform-azure-iac/app/bank-compliance/k8s/litellm/deployment.yaml)) are instrumented and monitored by Prometheus.

### Curated PromQL Cheatsheet

#### 1. Request Rate per Second (RPS) on FastAPI Backend:
```promql
sum(rate(http_requests_total{namespace="bank-compliance"}[2m])) by (handler, status)
```

#### 2. LiteLLM Proxy Request Latency (95th Percentile):
```promql
histogram_quantile(0.95, sum(rate(litellm_proxy_latency_bucket[5m])) by (le))
```

#### 3. Total LLM Token Consumption Rate (Prompt & Completion Tokens):
```promql
sum(rate(litellm_prompt_tokens[5m])) + sum(rate(litellm_completion_tokens[5m]))
```

#### 4. Pod Memory Usage vs Limit Percentage:
```promql
sum(container_memory_working_set_bytes{namespace="bank-compliance", container!=""}) by (pod)
/ 
sum(container_spec_memory_limit_bytes{namespace="bank-compliance", container!=""}) by (pod) * 100
```

#### 5. Pod CPU Throttling Rate:
```promql
sum(rate(container_cpu_cfs_throttled_periods_total{namespace="bank-compliance"}[5m])) by (pod)
/ 
sum(rate(container_cpu_cfs_periods_total{namespace="bank-compliance"}[5m])) by (pod) * 100
```

---

## 6. Resource Footprint & Cost Breakdown

| Component | CPU Request | CPU Limit | RAM Request | RAM Limit | Storage | Azure Cost Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Azure Monitor Agent (AMA)** | ~20m | ~100m | ~100Mi | ~256Mi | None (Ephemeral) | Free ingestion under 5GB/mo |
| **Prometheus Server** | 100m | 500m | 256Mi | 512Mi | 5GB Managed CSI | ~$0.50/month for 5GB disk |
| **Grafana Server** | 50m | 250m | 256Mi | 512Mi | 2GB Managed CSI | ~$0.20/month for 2GB disk |
| **Node Exporter + Kube-State** | 20m | 100m | 64Mi | 128Mi | None | $0 |
| **Total Overhead** | **~190m CPU** | **~950m CPU** | **~676Mi RAM** | **~1.4GB RAM** | **7GB Disk** | **< $1.00 / month total** |

---

## 7. Troubleshooting & FAQ

### Q1: How do I verify Prometheus is scraping the backend and LiteLLM?
Open Prometheus UI at `http://localhost:9090/targets`. Verify that:
* `serviceMonitor/bank-compliance/bankc-backend-monitor` shows state **UP (1/1)**.
* `serviceMonitor/bank-compliance/litellm-proxy-monitor` shows state **UP (1/1)**.

### Q2: Why did Grafana show "Failed to fetch" or restart?
If Grafana hits an `OOMKilled` (Out of Memory) exit code 137, ensure its memory limit is configured to at least `512Mi` in [`app/bank-compliance/k8s/monitoring/values.yaml`](file:///c:/Users/RichT/OneDrive/Documents/Repos/terraform-azure-iac/app/bank-compliance/k8s/monitoring/values.yaml#L52-L59). Then restart your port-forward:
```powershell
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

### Q3: Why does "Drilldown > Logs" show "Plugin failed to load"?
In Grafana, "Drilldown > Logs" requires **Grafana Loki**. In this architecture, all logs are streamed directly to **Azure Log Analytics (`law-ht-ss-p-cin-01`)** or viewed via `kubectl logs -n bank-compliance <pod-name> -f` to keep resource overhead at $0.00.

### Q4: What if I forget the Grafana password?
Reset it dynamically with `kubectl`:
```powershell
kubectl exec -it deployment/monitoring-grafana -n monitoring -c grafana -- grafana-cli admin reset-admin-password "NewSecurePassword123!"
```

### Q5: How do I cleanly uninstall Prometheus and Grafana?
```powershell
helm uninstall monitoring -n monitoring
kubectl delete namespace monitoring
```
