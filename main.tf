data "azurerm_resource_group" "hub" {
  name = var.hub_rg_name
}

data "azurerm_storage_account" "hub_state" {
  name                = var.hub_storage_account
  resource_group_name = data.azurerm_resource_group.hub.name
}

data "azurerm_key_vault" "hub" {
  count = var.key_vault_name == "" ? 0 : 1

  name                = var.key_vault_name
  resource_group_name = data.azurerm_resource_group.hub.name
}

resource "azurerm_virtual_network" "hub" {
  name                = var.hub_vnet_name
  resource_group_name = data.azurerm_resource_group.hub.name
  location            = var.location
  address_space       = var.hub_address_space
  tags                = local.tags
}

resource "azurerm_resource_group" "spoke" {
  name     = local.spoke_rg_name
  location = var.location
  tags     = local.tags
}

resource "azurerm_virtual_network" "spoke" {
  name                = local.spoke_vnet_name
  resource_group_name = azurerm_resource_group.spoke.name
  location            = azurerm_resource_group.spoke.location
  address_space       = var.spoke_address_space
  tags                = local.tags
}

resource "azurerm_subnet" "spoke" {
  for_each = var.spoke_subnets

  name                 = each.key
  resource_group_name  = azurerm_resource_group.spoke.name
  virtual_network_name = azurerm_virtual_network.spoke.name
  address_prefixes     = each.value.address_prefixes
}

resource "azurerm_virtual_network_peering" "spoke_to_hub" {
  name                      = "${azurerm_virtual_network.spoke.name}-to-${azurerm_virtual_network.hub.name}"
  resource_group_name       = azurerm_resource_group.spoke.name
  virtual_network_name      = azurerm_virtual_network.spoke.name
  remote_virtual_network_id = azurerm_virtual_network.hub.id
}

resource "azurerm_virtual_network_peering" "hub_to_spoke" {
  name                      = "${azurerm_virtual_network.hub.name}-to-${azurerm_virtual_network.spoke.name}"
  resource_group_name       = data.azurerm_resource_group.hub.name
  virtual_network_name      = azurerm_virtual_network.hub.name
  remote_virtual_network_id = azurerm_virtual_network.spoke.id
}

module "staticwebapi" {
  for_each = contains(keys(local.selected_apps), "staticwebapi") ? { staticwebapi = true } : {}

  source = "./apps/staticwebapi"

  resource_group_name = azurerm_resource_group.spoke.name
  environment         = var.environment
  location            = var.location
  subscription_id     = var.subscription_id
  tenant_id           = var.tenant_id
  vnet_id             = azurerm_virtual_network.spoke.id
  subnet_map          = { for name, subnet in azurerm_subnet.spoke : name => subnet.id }
  key_vault_ref       = local.key_vault_ref
  naming_prefix       = local.name_base
  instance_id         = "01"
  tags                = local.tags
}

module "serverless" {
  for_each = contains(keys(local.selected_apps), "serverless") ? { serverless = true } : {}

  source = "./apps/serverless"

  resource_group_name = azurerm_resource_group.spoke.name
  environment         = var.environment
  location            = var.location
  subscription_id     = var.subscription_id
  tenant_id           = var.tenant_id
  vnet_id             = azurerm_virtual_network.spoke.id
  subnet_map          = { for name, subnet in azurerm_subnet.spoke : name => subnet.id }
  key_vault_ref       = local.key_vault_ref
  naming_prefix       = local.name_base
  instance_id         = "01"
  tags                = local.tags
}

module "securems" {
  for_each = contains(keys(local.selected_apps), "securems") ? { securems = true } : {}

  source = "./apps/securems"

  resource_group_name = azurerm_resource_group.spoke.name
  environment         = var.environment
  location            = var.location
  subscription_id     = var.subscription_id
  tenant_id           = var.tenant_id
  vnet_id             = azurerm_virtual_network.spoke.id
  subnet_map          = { for name, subnet in azurerm_subnet.spoke : name => subnet.id }
  key_vault_ref       = local.key_vault_ref
  naming_prefix       = local.name_base
  instance_id         = "01"
  tags                = local.tags
}
