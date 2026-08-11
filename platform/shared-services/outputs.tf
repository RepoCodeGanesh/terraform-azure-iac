output "resource_group_name" {
  description = "Name of the shared services resource group."
  value       = azurerm_resource_group.shared_services.name
}

output "vnet_name" {
  description = "Name of the shared services VNet."
  value       = module.shared_vnet.vnet_name
}

output "subnet_ids" {
  description = "Subnet IDs created for the shared services VNet."
  value       = module.shared_vnet.subnet_ids
}

output "key_vault_name" {
  description = "Name of the shared Key Vault."
  value       = module.shared_key_vault.name
}

output "key_vault_id" {
  description = "ID of the shared Key Vault."
  value       = module.shared_key_vault.id
}

output "log_analytics_workspace_id" {
  description = "Resource ID of the shared Log Analytics workspace."
  value       = module.shared_log_analytics.id
}

output "apim_gateway_url" {
  description = "Gateway URL for the API Management instance."
  value       = module.shared_api_management.gateway_url
}

output "service_plan_name" {
  description = "Name of the App Service Plan."
  value       = module.shared_service_plan.name
}
