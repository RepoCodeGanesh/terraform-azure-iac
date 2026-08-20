# ==============================================================================
# Platform: Hub Network — Security & Cross-Subscription Workload Access
# Purpose: Grant Network Contributor on Hub VNet to App-Prod SP for VNet Peering
# ==============================================================================

resource "azurerm_role_assignment" "app_prod_hub_vnet_peering" {
  scope                = module.hub_vnet.vnet_id
  role_definition_name = "Network Contributor"
  principal_id         = var.app_prod_sp_object_id

  depends_on = [module.hub_vnet]
}
