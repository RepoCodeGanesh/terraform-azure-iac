output "id" {
  description = "Resource ID of the Linux Function App."
  value       = module.function_app.resource_id
  sensitive   = true
}

output "name" {
  description = "Name of the Linux Function App."
  value       = module.function_app.name
}

output "default_hostname" {
  description = "Default hostname of the Function App."
  value       = module.function_app.resource_uri
}

output "principal_id" {
  description = "System-Assigned Managed Identity Principal ID (if enabled)."
  value       = var.identity_type == "SystemAssigned" || var.identity_type == "SystemAssigned, UserAssigned" ? module.function_app.system_assigned_mi_principal_id : null
  sensitive   = true
}

output "storage_account_name" {
  description = "Backend Storage Account name."
  value       = azurerm_storage_account.this.name
}

output "storage_account_id" {
  description = "Backend Storage Account ID."
  value       = azurerm_storage_account.this.id
}

output "app_insights_instrumentation_key" {
  description = "Application Insights Instrumentation Key."
  value       = azurerm_application_insights.this.instrumentation_key
  sensitive   = true
}

output "app_insights_connection_string" {
  description = "Application Insights Connection String."
  value       = azurerm_application_insights.this.connection_string
  sensitive   = true
}
