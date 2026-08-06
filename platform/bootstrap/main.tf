terraform {
  backend "azurerm" {}
}

data "azurerm_client_config" "current" {}

############################################
# Naming Modules
############################################

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


############################################
# New Bootstrap
############################################

resource "azurerm_resource_group" "bootstrap_new" {
  name     = module.bootstrap_rg_name.name
  location = var.location
  tags     = local.tags
}

resource "azurerm_storage_account" "tfstate_new" {
  name                            = module.bootstrap_st_name.name
  resource_group_name             = azurerm_resource_group.bootstrap_new.name
  location                        = azurerm_resource_group.bootstrap_new.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  account_kind                    = "StorageV2"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = true
  https_traffic_only_enabled      = true
  shared_access_key_enabled       = true
  tags                            = local.tags

  blob_properties {
    delete_retention_policy {
      days = 1
    }

    container_delete_retention_policy {
      days = 1
    }
  }
}

resource "azurerm_storage_container" "tfstate_new" {
  name                  = var.tfstate_container_name
  storage_account_id    = azurerm_storage_account.tfstate_new.id
  container_access_type = "private"
}
