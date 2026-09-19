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
