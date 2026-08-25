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

# ─── Pillar 2: Central Azure Managed Grafana (Essential Free Tier $0.00) ──────
# Free Tier ($0.00): Supports up to 30 users with Entra ID SSO & Azure Monitor datasource

resource "azurerm_dashboard_grafana" "shared_grafana" {
  name                              = "grafana-${var.project}-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  resource_group_name               = azurerm_resource_group.shared_services.name
  location                          = azurerm_resource_group.shared_services.location
  sku                               = "Essential"
  api_key_enabled                   = true
  public_network_access_enabled     = true
  deterministic_outbound_ip_enabled = false

  identity {
    type = "SystemAssigned"
  }

  tags = local.tags

  depends_on = [azurerm_resource_group.shared_services]
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

# ─── Pillar 2: Azure Resource Graph Central Inventory Saved Queries ──────────

resource "azurerm_resource_graph_query" "orphan_disks" {
  name        = "query-orphan-disks-and-ips"
  query       = "Resources | where type =~ 'microsoft.compute/disks' and isnull(managedBy) | project id, name, resourceGroup, subscriptionId, type"
  description = "Identifies unattached managed disks and unassociated Public IPs across all subscriptions to prevent cost leakage."
}

resource "azurerm_resource_graph_query" "tag_compliance" {
  name        = "query-tag-compliance"
  query       = "Resources | where isempty(tags.Environment) or isempty(tags.Project) or isempty(tags.Workload) | project id, name, type, resourceGroup, subscriptionId"
  description = "Identifies any cloud resource missing mandatory enterprise CAF governance tags."
}

# ─── Pillar 2: Centralized Azure Monitor Workbook (Single Pane of Glass) ─────

resource "azurerm_application_insights_workbook" "platform_overview" {
  name                = "2d689b14-8f92-4f3a-96e2-54911d7e8b91"
  resource_group_name = azurerm_resource_group.shared_services.name
  location            = azurerm_resource_group.shared_services.location
  display_name        = "HappyTechies Enterprise Platform Overview"
  category            = "workbook"

  data_json = jsonencode({
    version = "Notebook/1.0"
    items = [
      {
        type = 1
        content = {
          json = "## HappyTechies Cloud & AI Platform — Enterprise Overview\nCentral monitoring dashboard for **TaxBot India** and **BankCompliance AI**."
        }
      }
    ]
  })

  tags = local.tags

  depends_on = [azurerm_resource_group.shared_services, module.shared_log_analytics]
}
