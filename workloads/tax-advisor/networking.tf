# ==============================================================================
# Workload: TaxBot India — Networking Tier
# Purpose: Spoke Virtual Network, App Integration Subnet, Private Endpoints & Hub Peering
# ==============================================================================

# ─── Spoke Virtual Network ─────────────────────────────────────────────────────

module "taxb_vnet" {
  source = "../../modules/network"

  resource_group_name = azurerm_resource_group.tax_advisor.name
  location            = azurerm_resource_group.tax_advisor.location
  vnet_name           = module.taxb_vnet_name.name
  address_space       = var.vnet_address_space

  subnet_names = [
    "snet-app-integration",
    "PrivateEndpoints"
  ]

  subnet_prefixes = [
    var.app_subnet_prefix,
    var.private_endpoints_subnet_prefix
  ]

  tags = local.tags
}

# ─── VNet Peering to Hub ───────────────────────────────────────────────────────

module "taxb_to_hub_peering" {
  source = "../../modules/vnet_peering"

  providers = {
    azurerm.vnet_1 = azurerm
    azurerm.vnet_2 = azurerm.hub
  }

  vnet_1_name = module.taxb_vnet.vnet_name
  vnet_1_rg   = azurerm_resource_group.tax_advisor.name
  vnet_1_id   = module.taxb_vnet.vnet_id

  vnet_2_name = data.azurerm_virtual_network.hub.name
  vnet_2_rg   = data.azurerm_resource_group.hub.name
  vnet_2_id   = data.azurerm_virtual_network.hub.id

  depends_on = [module.taxb_vnet]
}
