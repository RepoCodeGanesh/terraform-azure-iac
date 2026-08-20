# ==============================================================================
# Workload: TaxBot India — Observability & Alerting Tier
# Purpose: Diagnostic Settings, Operational Action Groups, and Cost-Safe Metric Alerts
# Cost:    Diagnostic ingestion free under 5GB LAW quota; active OpenAI rate limit guardian
# ==============================================================================

# ─── Diagnostic Settings: Azure AI Search ─────────────────────────────────────

resource "azurerm_monitor_diagnostic_setting" "search_diagnostics" {
  name                       = "ds-srch-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  target_resource_id         = module.search_service.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  enabled_log {
    category = "OperationLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

# ─── Diagnostic Settings: Cosmos DB ───────────────────────────────────────────

resource "azurerm_monitor_diagnostic_setting" "cosmos_diagnostics" {
  name                       = "ds-cosmos-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  target_resource_id         = module.cosmos_db.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  enabled_log {
    category = "DataPlaneRequests"
  }

  enabled_log {
    category = "QueryRuntimeStatistics"
  }

  enabled_log {
    category = "PartitionKeyRUConsumption"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

# ─── Diagnostic Settings: Shared Content Safety ───────────────────────────────

resource "azurerm_monitor_diagnostic_setting" "cs_diagnostics" {
  name                       = "ds-cs-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  target_resource_id         = data.azurerm_cognitive_account.content_safety.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  enabled_log {
    category = "Audit"
  }

  enabled_log {
    category = "RequestResponse"
  }

  enabled_metric {
    category = "AllMetrics"
  }

  depends_on = [
    data.azurerm_cognitive_account.content_safety,
    data.azurerm_log_analytics_workspace.shared
  ]
}

# ─── Action Group: Operations & Admin Email Notifications ─────────────────────

resource "azurerm_monitor_action_group" "taxb_ops" {
  name                = "ag-${var.workload}-ops-${var.environment}-${var.location_short}-${var.instance}"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  short_name          = "TaxbOps"

  email_receiver {
    name                    = "PrimaryOpsAdmin"
    email_address           = var.alert_email_address
    use_common_alert_schema = true
  }

  tags = local.tags
}

# ─── Metric Alert: Function App Server Errors (HTTP 5xx) ──────────────────────

resource "azurerm_monitor_metric_alert" "function_high_errors" {
  name                = "alert-func-high-5xx-errors"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  scopes              = [module.function_app.id]
  description         = "Triggers when Function App experiences > 5 server errors (HTTP 5xx) in 5 minutes."
  severity            = 1
  frequency           = "PT1M"
  window_size         = "PT5M"
  enabled             = false # Disabled to maintain $0.00 idle cost; enable as needed in production

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "Http5xx"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5
  }

  action {
    action_group_id = azurerm_monitor_action_group.taxb_ops.id
  }

  tags = local.tags
}

# ─── Metric Alert: OpenAI Rate Limiting & Throttling (HTTP 429) ───────────────

resource "azurerm_monitor_metric_alert" "openai_throttling" {
  name                = "alert-openai-throttled-429"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  scopes              = [data.azurerm_cognitive_account.openai.id]
  description         = "Triggers when Azure OpenAI rate limit (HTTP 429) throttling is encountered."
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"
  enabled             = true # Active primary quota & rate limit guardian (~$0.10/month)

  criteria {
    metric_namespace = "Microsoft.CognitiveServices/accounts"
    metric_name      = "BlockedCalls"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 1
  }

  action {
    action_group_id = azurerm_monitor_action_group.taxb_ops.id
  }

  tags = local.tags
}

# ─── Metric Alert: Content Safety Prompt Injection & Jailbreak Shield ─────────

resource "azurerm_monitor_metric_alert" "cs_jailbreak_alert" {
  name                = "alert-cs-jailbreak-detected"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  scopes              = [data.azurerm_cognitive_account.content_safety.id]
  description         = "Triggers when Azure AI Content Safety blocks >5 prompt injection/jailbreak attempts in 15 mins."
  severity            = 1
  frequency           = "PT5M"
  window_size         = "PT15M"
  enabled             = false # Disabled to maintain $0.00 idle cost; enable as needed in production

  criteria {
    metric_namespace = "Microsoft.CognitiveServices/accounts"
    metric_name      = "BlockedCalls"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5
  }

  action {
    action_group_id = azurerm_monitor_action_group.taxb_ops.id
  }

  tags = local.tags

  depends_on = [
    data.azurerm_cognitive_account.content_safety,
    azurerm_monitor_action_group.taxb_ops
  ]
}
