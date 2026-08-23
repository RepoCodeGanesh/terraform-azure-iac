output "id" {
  description = "ID of the Azure OpenAI Cognitive Account."
  value       = module.cognitive_account.resource_id
}

output "name" {
  description = "Name of the Azure OpenAI Cognitive Account."
  value       = var.name
}

output "endpoint" {
  description = "Endpoint URL of the Azure OpenAI Cognitive Account."
  value       = module.cognitive_account.endpoint
}

output "deployments" {
  description = "Map of created model deployments."
  value       = { for k, v in azurerm_cognitive_deployment.this : k => v.name }
}
