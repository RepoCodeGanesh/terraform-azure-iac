module "hub_vnet" {
  source  = "Azure/vnet/azurerm"
  version = "5.0.1"

  resource_group_name = var.resource_group_name
  use_for_each        = true
  vnet_location       = var.location
  vnet_name           = var.vnet_name
  address_space       = var.address_space
  subnet_names        = var.subnet_names
  subnet_prefixes     = var.subnet_prefixes
  tags                = var.tags
}
