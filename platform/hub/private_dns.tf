# ==============================================================================
# Platform: Hub Network — Central Private DNS Zones (Zero-Trust Resolution)
# Purpose: Shared private DNS resolution for Key Vault, AI Services, and AI Search
# Cost:    ~$0.50/month per zone (Enterprise CAF Hybrid DNS pattern)
# ==============================================================================

locals {
  private_dns_zones = [
    "privatelink.vaultcore.azure.net",
    "privatelink.cognitiveservices.azure.com",
    "privatelink.search.windows.net"
  ]
}

resource "azurerm_private_dns_zone" "hub_zones" {
  for_each            = toset(local.private_dns_zones)
  name                = each.key
  resource_group_name = azurerm_resource_group.hub.name
  tags                = local.tags
}

# ─── Hub VNet Link ────────────────────────────────────────────────────────────

resource "azurerm_private_dns_zone_virtual_network_link" "hub_vnet_links" {
  for_each              = azurerm_private_dns_zone.hub_zones
  name                  = "link-hub-${replace(each.key, ".", "-")}"
  resource_group_name   = azurerm_resource_group.hub.name
  private_dns_zone_name = each.value.name
  virtual_network_id    = module.hub_vnet.vnet_id
  registration_enabled  = false
  tags                  = local.tags
}
