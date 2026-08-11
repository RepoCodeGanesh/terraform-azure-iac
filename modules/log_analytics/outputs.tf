output "id" {
  description = "Log Analytics workspace resource ID."
  value       = azurerm_log_analytics_workspace.this.id
}

output "name" {
  description = "Log Analytics workspace name."
  value       = azurerm_log_analytics_workspace.this.name
}
