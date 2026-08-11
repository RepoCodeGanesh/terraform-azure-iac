terraform {
  required_providers {
    azurerm = {
      source                = "hashicorp/azurerm"
      version               = "~> 4.0"
      configuration_aliases = [azurerm.vnet_1, azurerm.vnet_2]
    }
  }
}

resource "azurerm_virtual_network_peering" "peering_1_to_2" {
  provider                     = azurerm.vnet_1
  name                         = "${var.vnet_1_name}-to-${var.vnet_2_name}"
  resource_group_name          = var.vnet_1_rg
  virtual_network_name         = var.vnet_1_name
  remote_virtual_network_id    = var.vnet_2_id
  allow_virtual_network_access = var.allow_virtual_network_access
  allow_forwarded_traffic      = var.allow_forwarded_traffic
}

resource "azurerm_virtual_network_peering" "peering_2_to_1" {
  provider                     = azurerm.vnet_2
  name                         = "${var.vnet_2_name}-to-${var.vnet_1_name}"
  resource_group_name          = var.vnet_2_rg
  virtual_network_name         = var.vnet_2_name
  remote_virtual_network_id    = var.vnet_1_id
  allow_virtual_network_access = var.allow_virtual_network_access
  allow_forwarded_traffic      = var.allow_forwarded_traffic
}
