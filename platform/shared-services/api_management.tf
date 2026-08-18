# ==============================================================================
# Platform: Shared Services — API Management & Hosting Plans
# Purpose: Shared API Gateway for external traffic routing and App Service Plan
# Cost:    $0.00 base cost (APIM Consumption_0 tier + F1 Free App Service Plan)
# ==============================================================================

# ─── Shared API Management Gateway ───────────────────────────────────────────

module "shared_api_management" {
  source = "../../modules/api_management"

  name                 = module.shared_apim_name.name
  location             = azurerm_resource_group.shared_services.location
  resource_group_name  = azurerm_resource_group.shared_services.name
  publisher_name       = var.publisher_name
  publisher_email      = var.publisher_email
  sku_name             = "Consumption_0"
  virtual_network_type = "None"
  public_ip_address_id = null
  tags                 = local.tags
}

resource "azurerm_monitor_diagnostic_setting" "apim_diagnostics" {
  name                       = "ds-${module.shared_apim_name.name}"
  target_resource_id         = module.shared_api_management.id
  log_analytics_workspace_id = module.shared_log_analytics.id

  enabled_log {
    category = "GatewayLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }

  depends_on = [
    module.shared_api_management,
    module.shared_log_analytics
  ]
}

# ─── Shared App Service Plan ──────────────────────────────────────────────────

module "shared_service_plan" {
  source = "../../modules/service_plan"

  name                = module.shared_asp_name.name
  location            = azurerm_resource_group.shared_services.location
  resource_group_name = azurerm_resource_group.shared_services.name
  os_type             = "Linux"
  sku_name            = "F1"
  tags                = local.tags
}
