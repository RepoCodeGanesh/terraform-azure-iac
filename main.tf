locals {
  hub_vnet_address_space = ["10.10.0.0/16"]
  app1_vnet_address_space = ["10.11.0.0/16"]
  app2_vnet_address_space = ["10.12.0.0/16"]

  hub_subnets = {
    "snet-shared" = {
      address_prefixes = ["10.10.0.0/24"]
    }
    "snet-private-endpoints" = {
      address_prefixes = ["10.10.1.0/24"]
    }
  }

  app1_subnets = {
    "snet-app" = {
      address_prefixes = ["10.11.0.0/24"]
    }
    "snet-private-endpoints" = {
      address_prefixes = ["10.11.1.0/24"]
    }
  }

  app2_subnets = {
    "snet-app" = {
      address_prefixes = ["10.12.0.0/24"]
    }
    "snet-private-endpoints" = {
      address_prefixes = ["10.12.1.0/24"]
    }
  }
}

data "azurerm_key_vault" "existing" {
  name                = var.existing_key_vault_name
  resource_group_name = var.hub_resource_group_name
}

module "hub_rg" {
  source   = "./modules/rg"
  name     = var.hub_resource_group_name
  location = var.location
  tags     = var.tags
}

module "hub_vnet" {
  source              = "./modules/vnet"
  name                = "ht-cind-${var.environment}-vnet-hub-01"
  resource_group_name = module.hub_rg.name
  location            = var.location
  address_space       = local.hub_vnet_address_space
  subnets             = local.hub_subnets
  tags                = var.tags
}

module "app1_rg" {
  source   = "./modules/rg"
  name     = "ht-centralindia-${var.environment}-rg-app1-01"
  location = var.location
  tags     = var.tags
}

module "app1_vnet" {
  source              = "./modules/vnet"
  name                = "ht-cind-${var.environment}-vnet-app1-01"
  resource_group_name = module.app1_rg.name
  location            = var.location
  address_space       = local.app1_vnet_address_space
  subnets             = local.app1_subnets
  tags                = var.tags
}

module "app1_storage" {
  source              = "./modules/storage_account"
  name                = "htc${var.environment}app1st${random_string.app1.result}"
  resource_group_name = module.app1_rg.name
  location            = var.location
  tags                = var.tags
}

module "app1_pe" {
  source                         = "./modules/private_endpoint"
  name                           = "pep-app1-blob-01"
  resource_group_name            = module.app1_rg.name
  location                       = var.location
  subnet_id                      = module.app1_vnet.subnet_ids["snet-private-endpoints"]
  virtual_network_id             = module.app1_vnet.vnet_id
  private_connection_resource_id = module.app1_storage.id
  subresource_names              = ["blob"]
  private_dns_zone_name          = "privatelink.blob.core.windows.net"
  tags                           = var.tags
}

module "app1_appservice" {
  source              = "./modules/app_service"
  name                = "ht-cind-${var.environment}-app1-web-01"
  resource_group_name = module.app1_rg.name
  location            = var.location
  tags                = var.tags
}

module "app1_to_hub_peering" {
  source                    = "./modules/vnet_peering"
  name                      = "peer-app1-to-hub"
  resource_group_name       = module.app1_rg.name
  virtual_network_name      = module.app1_vnet.vnet_name
  remote_virtual_network_id = module.hub_vnet.vnet_id
}

module "hub_to_app1_peering" {
  source                    = "./modules/vnet_peering"
  name                      = "peer-hub-to-app1"
  resource_group_name       = module.hub_rg.name
  virtual_network_name      = module.hub_vnet.vnet_name
  remote_virtual_network_id = module.app1_vnet.vnet_id
}

module "app2_rg" {
  source   = "./modules/rg"
  name     = "ht-centralindia-${var.environment}-rg-app2-01"
  location = var.location
  tags     = var.tags
}

module "app2_vnet" {
  source              = "./modules/vnet"
  name                = "ht-cind-${var.environment}-vnet-app2-01"
  resource_group_name = module.app2_rg.name
  location            = var.location
  address_space       = local.app2_vnet_address_space
  subnets             = local.app2_subnets
  tags                = var.tags
}

module "app2_storage" {
  source              = "./modules/storage_account"
  name                = "htc${var.environment}app2st${random_string.app2.result}"
  resource_group_name = module.app2_rg.name
  location            = var.location
  tags                = var.tags
}

module "app2_pe" {
  source                         = "./modules/private_endpoint"
  name                           = "pep-app2-blob-01"
  resource_group_name            = module.app2_rg.name
  location                       = var.location
  subnet_id                      = module.app2_vnet.subnet_ids["snet-private-endpoints"]
  virtual_network_id             = module.app2_vnet.vnet_id
  private_connection_resource_id = module.app2_storage.id
  subresource_names              = ["blob"]
  private_dns_zone_name          = "privatelink.blob.core.windows.net"
  tags                           = var.tags
}

module "app2_appservice" {
  source              = "./modules/app_service"
  name                = "ht-cind-${var.environment}-app2-web-01"
  resource_group_name = module.app2_rg.name
  location            = var.location
  tags                = var.tags
}

module "app2_to_hub_peering" {
  source                    = "./modules/vnet_peering"
  name                      = "peer-app2-to-hub"
  resource_group_name       = module.app2_rg.name
  virtual_network_name      = module.app2_vnet.vnet_name
  remote_virtual_network_id = module.hub_vnet.vnet_id
}

module "hub_to_app2_peering" {
  source                    = "./modules/vnet_peering"
  name                      = "peer-hub-to-app2"
  resource_group_name       = module.hub_rg.name
  virtual_network_name      = module.hub_vnet.vnet_name
  remote_virtual_network_id = module.app2_vnet.vnet_id
}

resource "random_string" "app1" {
  length  = 4
  upper   = false
  special = false
  numeric = true
}

resource "random_string" "app2" {
  length  = 4
  upper   = false
  special = false
  numeric = true
}
