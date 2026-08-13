output "id" {
  value       = azurerm_cognitive_account.content_safety.id
  description = "The ID of the Content Safety Cognitive Account."
}

output "name" {
  value       = azurerm_cognitive_account.content_safety.name
  description = "The name of the Content Safety Cognitive Account."
}

output "endpoint" {
  value       = azurerm_cognitive_account.content_safety.endpoint
  description = "The endpoint URL of the Content Safety Service."
}
