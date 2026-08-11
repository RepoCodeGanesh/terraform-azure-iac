output "peering_1_to_2_id" {
  description = "ID of the vnet peering from vnet 1 to vnet 2."
  value       = azurerm_virtual_network_peering.peering_1_to_2.id
}

output "peering_2_to_1_id" {
  description = "ID of the vnet peering from vnet 2 to vnet 1."
  value       = azurerm_virtual_network_peering.peering_2_to_1.id
}
