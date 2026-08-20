output "id" {
  description = "The ID of the Storage Account."
  value       = azurerm_storage_account.this.id
}

output "name" {
  description = "The Name of the Storage Account."
  value       = azurerm_storage_account.this.name
}

output "primary_blob_endpoint" {
  description = "The primary blob endpoint URL."
  value       = azurerm_storage_account.this.primary_blob_endpoint
}

output "primary_access_key" {
  description = "The primary access key for the storage account."
  value       = azurerm_storage_account.this.primary_access_key
  sensitive   = true
}

output "primary_connection_string" {
  description = "The connection string associated with the primary blob location."
  value       = azurerm_storage_account.this.primary_connection_string
  sensitive   = true
}

output "container_id" {
  description = "The ID of the created container (if container_name was specified)."
  value       = try(azurerm_storage_container.this[0].id, null)
}
