output "platform_management_group_id" {
  description = "Resource ID of the Platform Management Group"
  value       = azurerm_management_group.platform.id
}

output "landingzones_management_group_id" {
  description = "Resource ID of the Landing Zones Management Group"
  value       = azurerm_management_group.landingzones.id
}

output "enterprise_initiative_id" {
  description = "Resource ID of the Enterprise Governance Baseline Policy Set"
  value       = azurerm_management_group_policy_set_definition.enterprise_baseline.id
}

output "policy_assignment_id" {
  description = "Resource ID of the Management Group Policy Assignment"
  value       = azurerm_management_group_policy_assignment.baseline.id
}

output "amba_policy_definition_id" {
  description = "Resource ID of the AMBA Storage Baseline Policy Definition"
  value       = azurerm_policy_definition.amba_storage_availability.id
}

output "amba_policy_assignment_id" {
  description = "Resource ID of the AMBA Policy Assignment on Bootstrap"
  value       = azurerm_subscription_policy_assignment.amba_storage_bootstrap.id
}

output "amba_policy_identity_principal_id" {
  description = "Principal ID of the AMBA Policy Managed Identity"
  value       = azurerm_subscription_policy_assignment.amba_storage_bootstrap.identity[0].principal_id
}

