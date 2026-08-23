output "id" {
  description = "Resource ID of the Search Service."
  value       = azurerm_search_service.this.id
}

output "name" {
  description = "Name of the Search Service."
  value       = azurerm_search_service.this.name
}

output "endpoint" {
  description = "Primary endpoint URL of the Search Service."
  value       = "https://${var.name}.search.windows.net"
}
