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
