# ==============================================================================
# Workload: TaxBot India — AIOps & Autonomous Observability Tier
# Purpose: Azure Copilot Observability Agent for autonomous alert correlation and root-cause analysis
# ==============================================================================

# ─── Azure Monitor Workspace (Microsoft.Monitor/accounts) ─────────────────────
# Required by Azure Copilot Observability Agent for storing correlated metrics.

resource "azurerm_monitor_workspace" "observability" {
  count               = var.enable_observability_agent ? 1 : 0
  name                = module.taxb_amw_name.name
  resource_group_name = azurerm_resource_group.tax_advisor.name
  location            = var.observability_agent_location
  tags                = local.tags

  depends_on = [azurerm_resource_group.tax_advisor]
}

# ─── Azure Copilot Observability Agent (Autonomous Alert Correlation) ─────────

resource "azapi_resource" "observability_agent" {
  count                     = var.enable_observability_agent ? 1 : 0
  type                      = "Microsoft.Monitor/observabilityAgents@2026-05-01-preview"
  name                      = module.taxb_oa_name.name
  parent_id                 = azurerm_resource_group.tax_advisor.id
  location                  = var.observability_agent_location
  schema_validation_enabled = false

  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      monitoringAccountId = azurerm_monitor_workspace.observability[0].id
      enabled             = true
      customInstructions  = <<-EOT
        - TaxBot India ('taxb') uses Azure Functions, Azure OpenAI, and Cosmos DB.
        - Treat OpenAI 429 throttling (alert-openai-throttled-429) as an upstream rate limit event.
        - Group high 5xx server errors with upstream OpenAI throttling when occurring simultaneously.
      EOT
    }
  }

  tags = local.tags

  depends_on = [
    azurerm_monitor_workspace.observability,
    azurerm_resource_group.tax_advisor
  ]
}

# ─── Target Monitored Resource: Application Insights ──────────────────────────

resource "azapi_resource" "monitored_app_insights" {
  count                     = var.enable_observability_agent ? 1 : 0
  type                      = "Microsoft.Monitor/observabilityAgents/monitoredResources@2026-05-01-preview"
  name                      = "target-taxb-appi"
  parent_id                 = azapi_resource.observability_agent[0].id
  schema_validation_enabled = false

  body = {
    properties = {
      resourceId = module.function_app.app_insights_id
    }
  }

  depends_on = [azapi_resource.observability_agent]
}

# ─── Agent RBAC: Monitoring Reader Role ───────────────────────────────────────

resource "azurerm_role_assignment" "agent_monitoring_reader" {
  count                = var.enable_observability_agent ? 1 : 0
  scope                = azurerm_resource_group.tax_advisor.id
  role_definition_name = "Monitoring Reader"
  principal_id         = azapi_resource.observability_agent[0].identity[0].principal_id
}
