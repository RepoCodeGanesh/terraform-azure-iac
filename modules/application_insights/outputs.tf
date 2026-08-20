output "id" {
  description = "The ID of the Application Insights component."
  value       = azurerm_application_insights.this.id
}

output "name" {
  description = "The Name of the Application Insights component."
  value       = azurerm_application_insights.this.name
}

output "app_id" {
  description = "The App ID of Application Insights."
  value       = azurerm_application_insights.this.app_id
}

output "instrumentation_key" {
  description = "The Instrumentation Key of Application Insights."
  value       = azurerm_application_insights.this.instrumentation_key
  sensitive   = true
}

output "connection_string" {
  description = "The Connection String of Application Insights."
  value       = azurerm_application_insights.this.connection_string
  sensitive   = true
}
