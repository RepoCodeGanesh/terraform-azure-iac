##############################################################
# Wrapper module for Azure OpenAI (Cognitive Services Account)
# Source: Azure/avm-res-cognitiveservices-account/azurerm v0.11.1
# Azure Verified Module (AVM) - fully azurerm 4.x compatible
##############################################################

module "cognitive_account" {
  source  = "Azure/avm-res-cognitiveservices-account/azurerm"
  version = "0.11.1"

  name                          = var.name
  location                      = var.location
  parent_id                     = var.resource_group_id
  kind                          = "OpenAI"
  sku_name                      = var.sku_name
  custom_subdomain_name         = coalesce(var.custom_subdomain_name, var.name)
  public_network_access_enabled = var.public_network_access_enabled
  tags                          = var.tags
}

resource "azurerm_cognitive_deployment" "this" {
  for_each             = var.deployments
  name                 = each.key
  cognitive_account_id = module.cognitive_account.resource_id

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
  target_resource_id         = module.cognitive_account.resource_id
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
