data "azurerm_client_config" "current" {}

module "shared_rg_name" {
  source = "../../modules/naming"

  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_vnet_name" {
  source = "../../modules/naming"

  resource_type  = "vnet"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_kv_name" {
  source = "../../modules/naming"

  resource_type  = "kv"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_apim_name" {
  source = "../../modules/naming"

  resource_type  = "apim"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_law_name" {
  source = "../../modules/naming"

  resource_type  = "law"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_asp_name" {
  source = "../../modules/naming"

  resource_type  = "asp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

resource "azurerm_resource_group" "shared_services" {
  name     = module.shared_rg_name.name
  location = var.location
  tags     = local.tags
}

module "shared_vnet" {
  source = "../../modules/network"

  resource_group_name = azurerm_resource_group.shared_services.name
  location            = azurerm_resource_group.shared_services.location
  vnet_name           = module.shared_vnet_name.name
  address_space       = var.vnet_address_space

  subnet_names = [
    "Management",
    "SharedServices",
    "PrivateEndpoints"
  ]

  subnet_prefixes = [
    var.management_subnet_prefix,
    var.shared_services_subnet_prefix,
    var.private_endpoints_subnet_prefix
  ]

  tags = local.tags
}

module "shared_key_vault" {
  source = "../../modules/key_vault"

  name                          = module.shared_kv_name.name
  resource_group_name           = azurerm_resource_group.shared_services.name
  location                      = azurerm_resource_group.shared_services.location
  tenant_id                     = data.azurerm_client_config.current.tenant_id
  sku_name                      = "standard"
  enable_rbac_authorization     = true
  public_network_access_enabled = true
  purge_protection_enabled      = false
  soft_delete_retention_days    = 7
  tags                          = local.tags
}

module "shared_log_analytics" {
  source = "../../modules/log_analytics"

  name                = module.shared_law_name.name
  location            = azurerm_resource_group.shared_services.location
  resource_group_name = azurerm_resource_group.shared_services.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_analytics_retention_days
  tags                = local.tags
}

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

module "shared_service_plan" {
  source = "../../modules/service_plan"

  name                = module.shared_asp_name.name
  location            = azurerm_resource_group.shared_services.location
  resource_group_name = azurerm_resource_group.shared_services.name
  os_type             = "Linux"
  sku_name            = "F1"
  tags                = local.tags
}

############################################
# VNet Peering to Hub->
############################################

data "azurerm_resource_group" "hub" {
  provider = azurerm.hub
  name     = var.hub_resource_group_name
}

data "azurerm_virtual_network" "hub" {
  provider            = azurerm.hub
  name                = var.hub_vnet_name
  resource_group_name = data.azurerm_resource_group.hub.name
}

module "shared_to_hub_peering" {
  source = "../../modules/vnet_peering"

  providers = {
    azurerm.vnet_1 = azurerm
    azurerm.vnet_2 = azurerm.hub
  }

  vnet_1_name = module.shared_vnet.vnet_name
  vnet_1_rg   = azurerm_resource_group.shared_services.name
  vnet_1_id   = module.shared_vnet.vnet_id

  vnet_2_name = data.azurerm_virtual_network.hub.name
  vnet_2_rg   = data.azurerm_resource_group.hub.name
  vnet_2_id   = data.azurerm_virtual_network.hub.id

  depends_on = [
    module.shared_vnet
  ]
}

# ─── Grant app-prod SP write access to shared KV (for BankCompliance SWA token) ─
# The bank-compliance workload writes bankc-swa-deployment-token into this vault
# via provider = azurerm.shared. The app-prod SP needs Key Vault Secrets Officer
# so it can create/update that secret.

data "azuread_service_principal" "app_prod" {
  client_id = "99ab7987-3989-46c3-bae9-92279be16608" # DevOpsUniverse-Terraform-app-prod
}

resource "azurerm_role_assignment" "app_prod_kv_secrets_officer" {
  scope                = module.shared_key_vault.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azuread_service_principal.app_prod.object_id

  depends_on = [module.shared_key_vault]
}

# ─── Shared Azure AI Content Safety (F0 Free Tier) ────────────────────────────
# Single shared account consumed by all workloads via data source lookup.
# Lives in the shared-services sub (859a785c) — separate F0 quota from Apps-prod.

module "shared_cs_name" {
  source = "../../modules/naming"

  resource_type  = "cs"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.content_safety_location_short
  instance       = var.instance
}

module "shared_content_safety" {
  source = "../../modules/content_safety"

  name                = module.shared_cs_name.name
  location            = var.content_safety_location
  resource_group_name = azurerm_resource_group.shared_services.name
  sku_name            = "F0"
  tags                = local.tags

  depends_on = [azurerm_resource_group.shared_services]
}
