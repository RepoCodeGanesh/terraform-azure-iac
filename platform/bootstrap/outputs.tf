# ==============================================================================
# Platform: Bootstrap Outputs
# Formatted for immediate usability in remote state backend configuration
# ==============================================================================

output "resource_group_name" {
  description = "Bootstrap resource group name."
  value       = azurerm_resource_group.bootstrap_new.name
}

output "storage_account_name" {
  description = "Terraform state storage account name."
  value       = module.bootstrap_storage.name
}

output "storage_account_id" {
  description = "Terraform state storage account resource ID."
  value       = module.bootstrap_storage.id
}

output "primary_blob_endpoint" {
  description = "Primary Blob storage endpoint for state storage."
  value       = module.bootstrap_storage.primary_blob_endpoint
}

output "storage_container_name" {
  description = "Terraform state container name."
  value       = var.tfstate_container_name
}
