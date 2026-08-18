# ==============================================================================
# Platform: Shared Services — Networking Tier
# Purpose: Shared Spoke Virtual Network & Bi-Directional Hub VNet Peering
# ==============================================================================

# ─── Spoke Virtual Network & Subnets ──────────────────────────────────────────

module "shared_vnet" {
  source = "../../modules/network"

  resource_group_name = azurerm_resource_group.shared_services.name
  location            = azurerm_resource_group.shared_services.location
  vnet_name           = module.shared_vnet_name.name
  address_space       = var.vnet_address_space

  subnet_names = [
    "Management",
    "SharedServices",
    "PrivateEndpoints"
  ]

  subnet_prefixes = [
    var.management_subnet_prefix,
    var.shared_services_subnet_prefix,
    var.private_endpoints_subnet_prefix
  ]

  tags = local.tags
}

# ─── Hub Virtual Network Peering ──────────────────────────────────────────────

data "azurerm_resource_group" "hub" {
  provider = azurerm.hub
  name     = var.hub_resource_group_name
}

data "azurerm_virtual_network" "hub" {
  provider            = azurerm.hub
  name                = var.hub_vnet_name
  resource_group_name = data.azurerm_resource_group.hub.name
}

module "shared_to_hub_peering" {
  source = "../../modules/vnet_peering"

  providers = {
    azurerm.vnet_1 = azurerm
    azurerm.vnet_2 = azurerm.hub
  }

  vnet_1_name = module.shared_vnet.vnet_name
  vnet_1_rg   = azurerm_resource_group.shared_services.name
  vnet_1_id   = module.shared_vnet.vnet_id

  vnet_2_name = data.azurerm_virtual_network.hub.name
  vnet_2_rg   = data.azurerm_resource_group.hub.name
  vnet_2_id   = data.azurerm_virtual_network.hub.id

  depends_on = [
    module.shared_vnet
  ]
}
