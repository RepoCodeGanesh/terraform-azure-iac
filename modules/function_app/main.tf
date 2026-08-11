##############################################################
# Wrapper module for Azure Linux Function App
# Source: Azure/avm-res-web-site/azurerm ~> 0.22
# Azure Verified Module (AVM) – azapi-based, azurerm 4.x compatible
##############################################################

resource "azurerm_storage_account" "this" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_application_insights" "this" {
  name                = var.app_insights_name
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = var.log_analytics_workspace_id
  application_type    = "web"
  tags                = var.tags
}

module "function_app" {
  source  = "Azure/avm-res-web-site/azurerm"
  version = "~> 0.22"

  name                     = var.name
  location                 = var.location
  parent_id                = var.resource_group_id
  service_plan_resource_id = replace(var.service_plan_id, "serverFarms", "serverfarms")
  kind                     = "functionapp"
  public_network_access_enabled = var.public_network_access_enabled

  # Application Insights – passed from the inline resource above
  application_insights_key               = azurerm_application_insights.this.instrumentation_key
  application_insights_connection_string = azurerm_application_insights.this.connection_string

  # App settings merged with required Function App runtime setting
  app_settings = merge(
    var.app_settings,
    {
      "FUNCTIONS_WORKER_RUNTIME"                 = "python"
      "AzureWebJobsStorage"                      = azurerm_storage_account.this.primary_connection_string
      "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING" = azurerm_storage_account.this.primary_connection_string
      "WEBSITE_CONTENTSHARE"                     = lower(var.name)
    }
  )

  # Python runtime stack
  site_config = {
    always_on           = false
    minimum_tls_version = "1.3"

    application_stack = {
      python = {
        python_version = var.python_version
      }
    }
  }

  # Managed identity
  managed_identities = {
    system_assigned            = var.identity_type == "SystemAssigned" || var.identity_type == "SystemAssigned, UserAssigned"
    user_assigned_resource_ids = var.identity_type == "UserAssigned" || var.identity_type == "SystemAssigned, UserAssigned" ? toset(var.identity_ids) : toset([])
  }

  tags = var.tags
}
