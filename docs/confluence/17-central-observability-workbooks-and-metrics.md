# 17. Centralized Observability, Azure Monitor Workbooks & Telemetry Catalog

## 1. Metadata & Governance
* **Document ID:** SPEC-OBS-017
* **Architecture Tier:** Platform Observability, FinOps & Monitoring
* **Author / Tech Lead:** Enterprise Platform Engineering Team
* **Source Path:** `docs/confluence/17-central-observability-workbooks-and-metrics.md`
* **Central Workspace:** `law-ht-ss-p-cin-01` (Shared-Services sub `859a785c-...`)
* **Status:** Approved / Production-Hardened

---

## 2. Centralized Observability Architecture

The platform implements a **Hub-and-Spoke Observability Model** where all resource diagnostics, audit events, and application traces across the 4 CAF subscriptions stream into a single centralized Log Analytics Workspace:

```
+-----------------------------------------------------------------------------------------------+
|  SHARED-SERVICES SUBSCRIPTION (859a785c...)                                                   |
|                                                                                               |
|  +-----------------------------------------------------------------------------------------+  |
|  |  Central Log Analytics Workspace: law-ht-ss-p-cin-01                                     |  |
|  |  - Retention: 30 Days (FinOps Free Tier)                                                |  |
|  |  - Ingestion: 5.0 GB / month free quota                                                 |  |
|  +--------------------------------------------+--------------------------------------------+  |
+-----------------------------------------------|-----------------------------------------------+
                                                ^
                     Diagnostic Streaming Links | (Azure Diagnostic Settings)
        +---------------------------------------+---------------------------------------+
        |                                       |                                       |
+-------+-------------------------------+ +-----+-------------------------------+ +-----+-------------------------------+
| BOOTSTRAP (7689ad81)                  | | HUB-PROD (3eb8cc01)                 | | APPS-PROD (f4ffefe1)                  |
| - Terraform Remote State Storage      | | - Azure Firewall & Bastion          | | - AKS Cluster (aks-ht-bankc-p-cin-01)|
| - Bootstrap Key Vault Audit Logs      | | - Hub VNet Diagnostic Logs          | | - TaxBot Function App (AppRequests)  |
|   (AuditEvent)                        | |   (NetworkSecurityGroupRuleCounter) | | - Azure OpenAI & Cognitive Services   |
+---------------------------------------+ +-------------------------------------+ +---------------------------------------+
```

---

## 3. Azure Monitor Workbook: Single Pane of Glass

The centralized **Azure Monitor Workbook** (`2d689b14-8f92-4f3a-96e2-54911d7e8b91`) provides executive and engineering teams with real-time operational visibility across all workloads without requiring external commercial dashboards.

### Workbook Architecture & Cross-Component Binding:
When deploying workbooks at the Resource Group scope (`rg-ht-ss-p-cin-01`), each KQL query item must explicitly declare its target workspace via `crossComponentResources`:

```hcl
resource "azurerm_application_insights_workbook" "platform_overview" {
  name                = "2d689b14-8f92-4f3a-96e2-54911d7e8b91"
  resource_group_name = azurerm_resource_group.shared_services.name
  location            = azurerm_resource_group.shared_services.location
  display_name        = "HappyTechies Enterprise Platform Overview"
  category            = "workbook"

  data_json = jsonencode({
    version = "Notebook/1.0"
    items = [ ... ]
  })
}
```

> [!IMPORTANT]
> **Engineering Learning (Learning #34):** Omitting `crossComponentResources` causes queries to evaluate against the parent Resource Group (which has no KQL query provider), leaving the entire dashboard blank. Binding each item to `[module.shared_log_analytics.id]` guarantees immediate chart rendering.

---

## 4. Live Dashboard Panels & KQL Catalog

### Panel 1: TaxBot AI Application Requests & Latency
* **Target Table:** `AppRequests`
* **Visualization:** Timechart (Requests vs Errors)
* **KQL Query:**
  ```kql
  AppRequests
  | summarize
      TotalRequests = count(),
      Errors = countif(Success == false),
      AvgLatencyMs = round(avg(DurationMs), 1)
    by bin(TimeGenerated, 1h)
  | extend SuccessRate = round((TotalRequests - Errors) * 100.0 / TotalRequests, 1)
  | project TimeGenerated, TotalRequests, Errors, AvgLatencyMs
  | order by TimeGenerated asc
  ```

### Panel 2: AKS Cluster Resource Utilization (Node CPU % & Memory %)
* **Target Table:** `AzureMetrics`
* **Visualization:** Timechart
* **KQL Query:**
  ```kql
  AzureMetrics
  | where ResourceProvider == "MICROSOFT.CONTAINERSERVICE"
  | where MetricName in ("node_cpu_usage_percentage", "node_memory_working_set_percentage")
  | summarize AvgPercent = round(avg(Average), 1) by bin(TimeGenerated, 15m), MetricName
  | order by TimeGenerated asc
  ```

### Panel 3: AKS Control Plane Diagnostics & Audit Events
* **Target Table:** `AzureDiagnostics`
* **Visualization:** Multi-Series Area Timechart (>170k operations)
* **KQL Query:**
  ```kql
  AzureDiagnostics
  | where ResourceType == "MANAGEDCLUSTERS"
  | summarize OperationCount = count() by bin(TimeGenerated, 1h), Category
  | order by TimeGenerated asc
  ```

### Panel 4: AKS Pod Readiness & API Server Inflight Requests
* **Target Table:** `AzureMetrics`
* **Visualization:** Timechart
* **KQL Query:**
  ```kql
  AzureMetrics
  | where ResourceProvider == "MICROSOFT.CONTAINERSERVICE"
  | where MetricName in ("kube_pod_status_ready", "apiserver_current_inflight_requests")
  | summarize AvgValue = avg(Average) by bin(TimeGenerated, 30m), MetricName
  | order by TimeGenerated asc
  ```

---

## 5. FinOps Observability & Alerting Architecture

1. **Spend Control ($15/month Subscriptions):**
   * Configured via `azurerm_consumption_budget_subscription` across all 4 subscriptions.
   * Threshold alerts trigger at 70%, 90%, and 100% of forecast.
2. **Central Action Group (`ag-ht-ss-p-cin-01`):**
   * Configured in `platform/shared-services/observability.tf`.
   * Primary Administrator: `richtextforganesh@outlook.com`.
   * Uses Common Alert Schema (CAS) for standardized alert JSON payloads.
3. **Ingestion Quota Cap:**
   * Daily volume cap set to 0.166 GB/day (equivalent to 5 GB/month free tier), preventing unexpected runaway log charges.
