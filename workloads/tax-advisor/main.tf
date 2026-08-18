# ==============================================================================
# Workload: TaxBot India — Core & Naming
# Domain:   Conversational RAG Tax Advisor & Salary Optimizer (Income Tax India)
# Cost:     $0.00 base idle cost (Consumption Functions + Free Cosmos + Free SWA)
# ==============================================================================

data "azurerm_client_config" "current" {}

# ─── Shared Services & Hub Platform Lookups ───────────────────────────────────

data "azurerm_resource_group" "hub" {
  provider = azurerm.hub
  name     = var.hub_resource_group_name
}

data "azurerm_virtual_network" "hub" {
  provider            = azurerm.hub
  name                = var.hub_vnet_name
  resource_group_name = data.azurerm_resource_group.hub.name
}

data "azurerm_resource_group" "shared" {
  provider = azurerm.shared
  name     = var.shared_resource_group_name
}

data "azurerm_log_analytics_workspace" "shared" {
  provider            = azurerm.shared
  name                = var.shared_law_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

data "azurerm_api_management" "shared" {
  provider            = azurerm.shared
  name                = var.shared_apim_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

data "azurerm_key_vault" "shared" {
  provider            = azurerm.shared
  name                = var.shared_key_vault_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

# ─── CAF Resource Naming Modules ──────────────────────────────────────────────

module "taxb_rg_name" {
  source         = "../../modules/naming"
  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_vnet_name" {
  source         = "../../modules/naming"
  resource_type  = "vnet"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_asp_name" {
  source         = "../../modules/naming"
  resource_type  = "asp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_st_name" {
  source         = "../../modules/naming"
  resource_type  = "st"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_func_name" {
  source         = "../../modules/naming"
  resource_type  = "func"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_appi_name" {
  source         = "../../modules/naming"
  resource_type  = "appi"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_cosmos_name" {
  source         = "../../modules/naming"
  resource_type  = "cosmos"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_srch_name" {
  source         = "../../modules/naming"
  resource_type  = "srch"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_stapp_name" {
  source         = "../../modules/naming"
  resource_type  = "stapp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_oa_name" {
  source         = "../../modules/naming"
  resource_type  = "oa"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.observability_agent_location_short
  instance       = var.instance
}

module "taxb_amw_name" {
  source         = "../../modules/naming"
  resource_type  = "amw"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.observability_agent_location_short
  instance       = var.instance
}

# ─── Workload Resource Group ──────────────────────────────────────────────────

resource "azurerm_resource_group" "tax_advisor" {
  name     = module.taxb_rg_name.name
  location = var.location
  tags     = local.tags
}
