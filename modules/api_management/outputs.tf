output "gateway_url" {
  description = "Gateway URL for the API Management instance."
  value       = azurerm_api_management.this.gateway_url
}

output "name" {
  description = "API Management instance name."
  value       = azurerm_api_management.this.name
}
