# ==============================================================================
# Platform: Hub Network Outputs
# Formatted for immediate usability in spoke VNet peering & network topology
# ==============================================================================

output "resource_group_name" {
  description = "Hub resource group name."
  value       = azurerm_resource_group.hub.name
}

output "vnet_name" {
  description = "Hub virtual network name."
  value       = module.hub_vnet.vnet_name
}

output "vnet_id" {
  description = "Hub virtual network resource ID."
  value       = module.hub_vnet.vnet_id
}

output "subnet_ids" {
  description = "Hub subnet IDs."
  value       = module.hub_vnet.subnet_ids
}
