# ==============================================================================
# Platform: Shared Services — Core & Naming
# Subscription: Shared-services (859a785c-bd38-402d-b595-1f44f40fb9bf)
# Purpose: Shared platform foundation (Resource Group & CAF Naming lookups)
# ==============================================================================

data "azurerm_client_config" "current" {}

# ─── CAF Resource Naming Modules ──────────────────────────────────────────────

module "shared_rg_name" {
  source         = "../../modules/naming"
  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_vnet_name" {
  source         = "../../modules/naming"
  resource_type  = "vnet"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_kv_name" {
  source         = "../../modules/naming"
  resource_type  = "kv"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_apim_name" {
  source         = "../../modules/naming"
  resource_type  = "apim"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_law_name" {
  source         = "../../modules/naming"
  resource_type  = "law"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_asp_name" {
  source         = "../../modules/naming"
  resource_type  = "asp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "shared_cs_name" {
  source         = "../../modules/naming"
  resource_type  = "cs"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.content_safety_location_short
  instance       = var.instance
}

module "shared_oai_name" {
  source         = "../../modules/naming"
  resource_type  = "oai"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.openai_location_short
  instance       = var.instance
}

# ─── Shared Services Resource Group ───────────────────────────────────────────

resource "azurerm_resource_group" "shared_services" {
  name     = module.shared_rg_name.name
  location = var.location
  tags     = local.tags
}
