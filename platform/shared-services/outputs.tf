# ==============================================================================
# Platform: Shared Services Outputs
# Formatted for immediate usability in downstream workload roots & pipelines
# ==============================================================================

output "resource_group_name" {
  description = "Name of the shared services resource group."
  value       = azurerm_resource_group.shared_services.name
}

output "vnet_name" {
  description = "Name of the shared services VNet."
  value       = module.shared_vnet.vnet_name
}

output "subnet_ids" {
  description = "Subnet IDs created for the shared services VNet."
  value       = module.shared_vnet.subnet_ids
}

output "key_vault_name" {
  description = "Name of the shared Key Vault."
  value       = module.shared_key_vault.name
}

output "key_vault_id" {
  description = "ID of the shared Key Vault."
  value       = module.shared_key_vault.id
}

output "key_vault_uri" {
  description = "Vault URI of the shared Key Vault."
  value       = module.shared_key_vault.vault_uri
}

output "log_analytics_workspace_id" {
  description = "Resource ID of the shared Log Analytics workspace."
  value       = module.shared_log_analytics.id
}

output "apim_gateway_url" {
  description = "Gateway URL for the API Management instance."
  value       = startswith(module.shared_api_management.gateway_url, "https://") ? module.shared_api_management.gateway_url : "https://${module.shared_api_management.gateway_url}"
}

output "content_safety_name" {
  description = "Name of the shared Azure AI Content Safety account."
  value       = module.shared_content_safety.name
}

output "content_safety_endpoint" {
  description = "Endpoint URL of the shared Azure AI Content Safety account."
  value       = module.shared_content_safety.endpoint
}

output "content_safety_id" {
  description = "Resource ID of the shared Azure AI Content Safety account."
  value       = module.shared_content_safety.id
}

output "openai_name" {
  description = "Name of the shared Azure OpenAI account."
  value       = module.shared_openai.name
}

output "openai_endpoint" {
  description = "Endpoint URL of the shared Azure OpenAI account."
  value       = module.shared_openai.endpoint
}

output "openai_model_name" {
  description = "Deployed model name on the shared Azure OpenAI account."
  value       = var.openai_model_name
}

output "doc_intelligence_endpoint" {
  description = "Endpoint URL of the shared Azure AI Document Intelligence account."
  value       = azurerm_cognitive_account.shared_doc_intelligence.endpoint
}


output "action_group_id" {
  description = "Resource ID of the central Monitor Action Group for enterprise alerts."
  value       = azurerm_monitor_action_group.central_alerts.id
}
