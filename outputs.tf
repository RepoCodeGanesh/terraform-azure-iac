output "naming_prefix" {
  description = "Normalized base name used by the dev learning repo."
  value       = local.name_base
}

output "spoke" {
  description = "Created spoke resource identifiers."
  value = {
    resource_group_name = azurerm_resource_group.spoke.name
    vnet_id             = azurerm_virtual_network.spoke.id
    subnets             = { for name, subnet in azurerm_subnet.spoke : name => subnet.id }
  }
}

output "hub" {
  description = "Created hub VNet and existing hub references."
  value = {
    resource_group_name = data.azurerm_resource_group.hub.name
    vnet_id             = azurerm_virtual_network.hub.id
    vnet_name           = azurerm_virtual_network.hub.name
    storage_account_id  = data.azurerm_storage_account.hub_state.id
    key_vault_id        = try(data.azurerm_key_vault.hub[0].id, null)
  }
}

output "module_outputs" {
  description = "Outputs from enabled app modules."
  value = {
    staticwebapi = try(module.staticwebapi["staticwebapi"], null)
    serverless   = try(module.serverless["serverless"], null)
    securems     = try(module.securems["securems"], null)
  }
}
