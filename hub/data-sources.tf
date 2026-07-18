data "azurerm_resource_group" "hub" {
  name = var.hub_rg_name
}

data "azurerm_storage_account" "hub_state" {
  name                = var.hub_storage_account
  resource_group_name = data.azurerm_resource_group.hub.name
}

data "azurerm_key_vault" "hub" {
  name                = var.key_vault_name
  resource_group_name = data.azurerm_resource_group.hub.name
}
