output "resource_group_name" {
  description = "The created resource group name."
  value       = azurerm_resource_group.this.name
}

output "resource_group_id" {
  description = "The created resource group ID."
  value       = azurerm_resource_group.this.id
}

output "tags" {
  description = "The merged tag map for downstream resources."
  value       = local.merged_tags
}
