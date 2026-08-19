output "id" {
  description = "The ID of the Static Web App."
  value       = azurerm_static_web_app.this.id
}

output "name" {
  description = "The Name of the Static Web App."
  value       = azurerm_static_web_app.this.name
}

output "default_host_name" {
  description = "The default host name of the Static Web App."
  value       = azurerm_static_web_app.this.default_host_name
}

output "api_key" {
  description = "The API key (deployment token) used for GitHub Actions / CI/CD deployment."
  value       = azurerm_static_web_app.this.api_key
  sensitive   = true
}

output "custom_domain_name" {
  description = "The verified custom domain name attached to the Static Web App."
  value       = length(azurerm_static_web_app_custom_domain.this) > 0 ? azurerm_static_web_app_custom_domain.this[0].domain_name : null
}
