output "id" {
  description = "ID of the Azure OpenAI Cognitive Account."
  value       = azurerm_cognitive_account.this.id
}

output "name" {
  description = "Name of the Azure OpenAI Cognitive Account."
  value       = azurerm_cognitive_account.this.name
}

output "endpoint" {
  description = "Endpoint URL of the Azure OpenAI Cognitive Account."
  value       = azurerm_cognitive_account.this.endpoint
}

output "deployments" {
  description = "Map of created model deployments."
  value       = { for k, v in azurerm_cognitive_deployment.this : k => v.name }
}
