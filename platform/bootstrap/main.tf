# ==============================================================================
# Platform: Bootstrap — Core & Remote State Storage
# Subscription: bootstrap (7689ad81-71ba-481b-a17c-e1b6be61bab1)
# Purpose: Remote Terraform state storage account & Key Vault backend
# Cost:    Standard LRS ($0 base cost, pennies per month for state storage)
# ==============================================================================

terraform {
  backend "azurerm" {}
}

data "azurerm_client_config" "current" {}

# ─── CAF Resource Naming Modules ──────────────────────────────────────────────

module "bootstrap_rg_name" {
  source = "../../modules/naming"

  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "bootstrap_st_name" {
  source = "../../modules/naming"

  resource_type  = "st"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

# ─── Bootstrap Resource Group ─────────────────────────────────────────────────

resource "azurerm_resource_group" "bootstrap_new" {
  name     = module.bootstrap_rg_name.name
  location = var.location
  tags     = local.tags
}

# ─── Remote State Storage Account & Container ─────────────────────────────────

module "bootstrap_storage" {
  source = "../../modules/storage_account"

  name                          = module.bootstrap_st_name.name
  resource_group_name           = azurerm_resource_group.bootstrap_new.name
  location                      = azurerm_resource_group.bootstrap_new.location
  account_tier                  = "Standard"
  account_replication_type      = "LRS"
  account_kind                  = "StorageV2"
  public_network_access_enabled = true
  shared_access_key_enabled     = true
  blob_retention_days           = 1
  container_retention_days      = 1
  container_name                = var.tfstate_container_name
  container_access_type         = "private"
  tags                          = local.tags
}

# ─── State Migration Blocks (Zero-Breakage Guarantee) ─────────────────────────

moved {
  from = azurerm_storage_account.tfstate_new
  to   = module.bootstrap_storage.azurerm_storage_account.this
}

moved {
  from = azurerm_storage_container.tfstate_new
  to   = module.bootstrap_storage.azurerm_storage_container.this[0]
}
