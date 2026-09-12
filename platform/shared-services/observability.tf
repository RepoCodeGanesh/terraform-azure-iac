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
          json = "## HappyTechies Cloud & AI Platform — Enterprise Observability\n\nReal-time monitoring for **TaxBot India** and **BankCompliance AI** workloads.\n\n> **Workspace:** `law-ht-ss-p-cin-01` (Shared-Services Subscription)"
        }
      },

      # ── Panel 1: AI Request Rate & Error Rate (5-min timechart) ──────────────
      {
        type    = 3
        name    = "ai-request-rate-error-rate"
        content = {
          version = "KqlItem/1.0"
          query   = <<-KQL
            ContainerLog
            | where LogEntry has "POST /api/v1/compliance" or LogEntry has "status_code"
            | extend IsError = LogEntry has "ERROR" or LogEntry has "HTTP 5" or LogEntry has "status=5"
            | summarize
                TotalRequests = count(),
                Errors = countif(IsError)
              by bin(TimeGenerated, 5m)
            | extend SuccessRate = round((TotalRequests - Errors) * 100.0 / TotalRequests, 1)
            | project TimeGenerated, TotalRequests, Errors, SuccessRate
            | order by TimeGenerated asc
          KQL
          size        = 0
          title       = "AI Request Rate & Error Rate (5-min buckets)"
          timeContext = { durationMs = 3600000 }
          queryType   = 0
          resourceType = "microsoft.operationalinsights/workspaces"
          visualization = "timechart"
          chartSettings = {
            yAxis = [
              { column = "TotalRequests", label = "Requests", color = "blue-2" },
              { column = "Errors", label = "Errors", color = "red-3" }
            ]
          }
        }
      },

      # ── Panel 2: Response Latency P50 / P95 / P99 (15-min timechart) ─────────
      {
        type    = 3
        name    = "latency-percentiles"
        content = {
          version = "KqlItem/1.0"
          query   = <<-KQL
            ContainerLog
            | where LogEntry matches regex @"duration_ms=[0-9]+"
            | extend LatencyMs = todouble(extract(@"duration_ms=([0-9]+\.?[0-9]*)", 1, LogEntry))
            | where isnotnull(LatencyMs) and LatencyMs > 0
            | summarize
                P50 = percentile(LatencyMs, 50),
                P95 = percentile(LatencyMs, 95),
                P99 = percentile(LatencyMs, 99)
              by bin(TimeGenerated, 15m)
            | order by TimeGenerated asc
          KQL
          size        = 0
          title       = "Agent Response Latency — P50 / P95 / P99 (15-min buckets)"
          timeContext = { durationMs = 14400000 }
          queryType   = 0
          resourceType = "microsoft.operationalinsights/workspaces"
          visualization = "timechart"
          chartSettings = {
            yAxis = [
              { column = "P50", label = "P50 (ms)", color = "green-2" },
              { column = "P95", label = "P95 (ms)", color = "yellow-3" },
              { column = "P99", label = "P99 (ms)", color = "red-2" }
            ]
          }
        }
      },

      # ── Panel 3: Qdrant Vector Search Activity (10-min barchart) ─────────────
      {
        type    = 3
        name    = "qdrant-activity"
        content = {
          version = "KqlItem/1.0"
          query   = <<-KQL
            ContainerLog
            | where ContainerName has "qdrant" or LogEntry has "qdrant" or LogEntry has "vector_search"
            | where LogEntry has "search" or LogEntry has "retrieved" or LogEntry has "clauses"
            | extend IsHit  = LogEntry has "retrieved" or LogEntry has "clauses found"
            | extend IsMiss = LogEntry has "No clauses" or LogEntry has "0 results"
            | summarize
                SearchCalls = count(),
                CacheHits   = countif(IsHit),
                CacheMisses = countif(IsMiss)
              by bin(TimeGenerated, 10m)
            | order by TimeGenerated asc
          KQL
          size        = 0
          title       = "Qdrant Vector Search Activity — Calls / Hits / Misses (10-min)"
          timeContext = { durationMs = 7200000 }
          queryType   = 0
          resourceType = "microsoft.operationalinsights/workspaces"
          visualization = "barchart"
        }
      },

      # ── Panel 4: Pod Status Timeline (bank-compliance namespace) ─────────────
      {
        type    = 3
        name    = "pod-status-timeline"
        content = {
          version = "KqlItem/1.0"
          query   = <<-KQL
            KubePodInventory
            | where Namespace == "bank-compliance"
            | summarize
                RunningPods   = countif(PodStatus == "Running"),
                PendingPods   = countif(PodStatus == "Pending"),
                FailedPods    = countif(PodStatus == "Failed"),
                UnknownPods   = countif(PodStatus !in ("Running", "Pending", "Succeeded", "Failed"))
              by bin(TimeGenerated, 5m), Name
            | order by TimeGenerated asc
          KQL
          size        = 0
          title       = "Pod Status Timeline — bank-compliance Namespace"
          timeContext = { durationMs = 3600000 }
          queryType   = 0
          resourceType = "microsoft.operationalinsights/workspaces"
          visualization = "timechart"
          chartSettings = {
            yAxis = [
              { column = "RunningPods",  label = "Running",  color = "green-2" },
              { column = "PendingPods",  label = "Pending",  color = "yellow-2" },
              { column = "FailedPods",   label = "Failed",   color = "red-3" }
            ]
          }
        }
      }
    ]
  })

  tags = local.tags

  depends_on = [azurerm_resource_group.shared_services, module.shared_log_analytics]
}

