# ==============================================================================
# Workload: BankCompliance AI — Networking Tier
# Purpose: Spoke Virtual Network, AKS Subnet, Private Endpoints & Peering to Hub
# ==============================================================================

# ─── Spoke Virtual Network & Subnets ──────────────────────────────────────────

module "bankc_vnet" {
  source = "../../modules/network"

  resource_group_name = azurerm_resource_group.bank_compliance.name
  location            = azurerm_resource_group.bank_compliance.location
  vnet_name           = module.bankc_vnet_name.name
  address_space       = var.vnet_address_space

  subnet_names = [
    "snet-aks",
    "snet-pe"
  ]

  subnet_prefixes = [
    var.aks_subnet_prefix,
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

module "spoke_to_hub_peering" {
  source = "../../modules/vnet_peering"

  providers = {
    azurerm.vnet_1 = azurerm
    azurerm.vnet_2 = azurerm.hub
  }

  vnet_1_name = module.bankc_vnet.vnet_name
  vnet_1_rg   = azurerm_resource_group.bank_compliance.name
  vnet_1_id   = module.bankc_vnet.vnet_id

  vnet_2_name = data.azurerm_virtual_network.hub.name
  vnet_2_rg   = data.azurerm_resource_group.hub.name
  vnet_2_id   = data.azurerm_virtual_network.hub.id

  depends_on = [
    module.bankc_vnet
  ]
}
