output "id" {
  description = "App Service Plan resource ID."
  value       = azurerm_service_plan.this.id
}

output "name" {
  description = "App Service Plan name."
  value       = azurerm_service_plan.this.name
}
