output "backend_id" {
  description = "The ID of the APIM Backend."
  value       = azurerm_api_management_backend.this.id
}

output "api_id" {
  description = "The ID of the published APIM API."
  value       = azapi_resource.api.id
}

output "path" {
  description = "The path suffix of the published API."
  value       = var.path
}
