data "azurerm_client_config" "current" {}

module "hub_rg_name" {
  source = "../../modules/naming"

  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "hub_vnet_name" {
  source = "../../modules/naming"

  resource_type  = "vnet"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

resource "azurerm_resource_group" "hub" {
  name     = module.hub_rg_name.name
  location = var.location
  tags     = local.tags
}

module "hub_vnet" {
  source = "../../modules/network"

  resource_group_name = azurerm_resource_group.hub.name
  location            = azurerm_resource_group.hub.location
  vnet_name           = module.hub_vnet_name.name
  address_space       = var.vnet_address_space
  subnet_names = [
    "AzureFirewallSubnet",
    "AzureBastionSubnet",
    "GatewaySubnet",
    "Management"
  ]
  subnet_prefixes = [
    var.firewall_subnet_prefix,
    var.bastion_subnet_prefix,
    var.gateway_subnet_prefix,
    var.management_subnet_prefix
  ]
  tags = local.tags
}
