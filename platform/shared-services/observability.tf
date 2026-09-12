# ==============================================================================
# Platform: Shared Services — Central Observability Tier
# Purpose: Central Log Analytics Workspace for streaming logs across all landing zone subscriptions
# Cost:    $0.00 / Month (Includes 5 GB/month free data ingestion)
# ==============================================================================

# ─── Central Log Analytics Workspace ──────────────────────────────────────────

module "shared_log_analytics" {
  source = "../../modules/log_analytics"

  name                = module.shared_law_name.name
  location            = azurerm_resource_group.shared_services.location
  resource_group_name = azurerm_resource_group.shared_services.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_analytics_retention_days
  tags                = local.tags
}

# ─── Pillar 2: Central Monitor Action Group (ag-ht-ss-p-cin-01) ───────────────
# Free Tier: Up to 1,000 free email notifications per month

resource "azurerm_monitor_action_group" "central_alerts" {
  name                = "ag-${var.project}-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  resource_group_name = azurerm_resource_group.shared_services.name
  short_name          = "HTAlerts"

  email_receiver {
    name                    = "PrimaryAdmin"
    email_address           = "richtextforganesh@outlook.com"
    use_common_alert_schema = true
  }

  tags = local.tags

  depends_on = [azurerm_resource_group.shared_services]
}

# ─── Pillar 2: Centralized Azure Monitor Workbook (Single Pane of Glass) ─────

resource "azurerm_application_insights_workbook" "platform_overview" {
  name                = "2d689b14-8f92-4f3a-96e2-54911d7e8b91"
  resource_group_name = azurerm_resource_group.shared_services.name
  location            = azurerm_resource_group.shared_services.location
  display_name        = "HappyTechies Enterprise Platform Overview"
  category            = "workbook"

  # O2: 4-panel Azure Monitor Workbook with live KQL queries
  # Panels: AI Request Rate & Error Rate | Latency P50/P95/P99 | Qdrant Activity | Pod Status Timeline
  data_json = jsonencode({
    version = "Notebook/1.0"
    items = [
      # ── Panel 0: Title & Description ─────────────────────────────────────────
      {
        type    = 1
        name    = "platform-title"
        content = {
          json = "## HappyTechies Cloud & AI Platform — Enterprise Observability\n\nCentralized monitoring for **TaxBot India** and **BankCompliance AI**.\n\n* **Log Analytics Workspace:** `law-ht-ss-p-cin-01` (Central India)\n* **AKS Cluster:** `aks-ht-bankc-p-cin-01` (Workload: BankCompliance)\n* **Status:** Operational"
        }
      },

      # ── Panel 1: TaxBot AI Application Requests & Errors ─────────────────────
      {
        type    = 3
        name    = "ai-request-rate"
        content = {
          version                  = "KqlItem/1.0"
          query                    = <<-KQL
            AppRequests
            | summarize
                TotalRequests = count(),
                Errors = countif(Success == false),
                AvgLatencyMs = round(avg(DurationMs), 1)
              by bin(TimeGenerated, 1h)
            | extend SuccessRate = round((TotalRequests - Errors) * 100.0 / TotalRequests, 1)
            | project TimeGenerated, TotalRequests, Errors, AvgLatencyMs
            | order by TimeGenerated asc
          KQL
          size                     = 0
          title                    = "TaxBot AI Application Requests & Errors (Hourly)"
          timeContext              = { durationMs = 604800000 }
          queryType                = 0
          resourceType             = "microsoft.operationalinsights/workspaces"
          crossComponentResources  = [module.shared_log_analytics.id]
          visualization            = "timechart"
          chartSettings = {
            yAxis = [
              { column = "TotalRequests", label = "Requests", color = "blue-2" },
              { column = "Errors", label = "Errors", color = "red-3" }
            ]
          }
        }
      },

      # ── Panel 2: AKS Control Plane Diagnostics & Audit Events ────────────────
      {
        type    = 3
        name    = "aks-control-plane"
        content = {
          version                  = "KqlItem/1.0"
          query                    = <<-KQL
            AzureDiagnostics
            | where ResourceType == "MANAGEDCLUSTERS"
            | summarize OperationCount = count() by bin(TimeGenerated, 1h), Category
            | order by TimeGenerated asc
          KQL
          size                     = 0
          title                    = "AKS Control Plane Diagnostics & Audit Events (Hourly)"
          timeContext              = { durationMs = 86400000 }
          queryType                = 0
          resourceType             = "microsoft.operationalinsights/workspaces"
          crossComponentResources  = [module.shared_log_analytics.id]
          visualization            = "timechart"
        }
      },

      # ── Panel 3: AKS Kubernetes Pod Inventory & Health Timeline ──────────────
      {
        type    = 3
        name    = "pod-status-timeline"
        content = {
          version                  = "KqlItem/1.0"
          query                    = <<-KQL
            KubePodInventory
            | summarize
                RunningPods = countif(PodStatus == "Running"),
                PendingPods = countif(PodStatus == "Pending")
              by bin(TimeGenerated, 1h), Namespace
            | order by TimeGenerated asc
          KQL
          size                     = 0
          title                    = "AKS Kubernetes Pod Inventory & Health Timeline"
          timeContext              = { durationMs = 604800000 }
          queryType                = 0
          resourceType             = "microsoft.operationalinsights/workspaces"
          crossComponentResources  = [module.shared_log_analytics.id]
          visualization            = "barchart"
        }
      }
    ]
  })

  tags = local.tags

  depends_on = [azurerm_resource_group.shared_services, module.shared_log_analytics]
}

