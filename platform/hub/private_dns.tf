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

# ─── Shared Services Spoke VNet Link ──────────────────────────────────────────

resource "azurerm_private_dns_zone_virtual_network_link" "shared_services_vnet_links" {
  for_each              = azurerm_private_dns_zone.hub_zones
  name                  = "link-ss-${replace(each.key, ".", "-")}"
  resource_group_name   = azurerm_resource_group.hub.name
  private_dns_zone_name = each.value.name
  virtual_network_id    = "/subscriptions/859a785c-bd38-402d-b595-1f44f40fb9bf/resourceGroups/rg-ht-ss-p-cin-01/providers/Microsoft.Network/virtualNetworks/vnet-ht-ss-p-cin-01"
  registration_enabled  = false
  tags                  = local.tags
}

# ─── Apps Spoke VNet Link (BankCompliance AKS) ────────────────────────────────

resource "azurerm_private_dns_zone_virtual_network_link" "apps_vnet_links" {
  for_each              = azurerm_private_dns_zone.hub_zones
  name                  = "link-apps-${replace(each.key, ".", "-")}"
  resource_group_name   = azurerm_resource_group.hub.name
  private_dns_zone_name = each.value.name
  virtual_network_id    = "/subscriptions/f4ffefe1-d689-4059-969c-ccc73e2a11d4/resourceGroups/rg-ht-bankc-p-cin-01/providers/Microsoft.Network/virtualNetworks/vnet-ht-bankc-p-cin-01"
  registration_enabled  = false
  tags                  = local.tags
}
