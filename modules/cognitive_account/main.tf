resource "azurerm_cognitive_account" "this" {
  name                          = var.name
  location                      = var.location
  resource_group_name           = split("/", var.resource_group_id)[4]
  kind                          = "OpenAI"
  sku_name                      = var.sku_name
  custom_subdomain_name         = coalesce(var.custom_subdomain_name, var.name)
  public_network_access_enabled = var.public_network_access_enabled
  tags                          = var.tags
}

resource "azurerm_cognitive_deployment" "this" {
  for_each             = var.deployments
  name                 = each.key
  cognitive_account_id = azurerm_cognitive_account.this.id

  model {
    format  = each.value.model_format
    name    = each.value.model_name
    version = each.value.model_version
  }

  sku {
    name     = each.value.sku_name
    capacity = each.value.sku_capacity
  }
}

resource "azurerm_monitor_diagnostic_setting" "this" {
  count                      = var.log_analytics_workspace_id != null ? 1 : 0
  name                       = "ds-${var.name}-telemetry"
  target_resource_id         = azurerm_cognitive_account.this.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "Audit"
  }

  enabled_log {
    category = "RequestResponse"
  }

  enabled_log {
    category = "Trace"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}
