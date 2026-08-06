output "resource_group_name" {
  description = "Name of the DevOnboard AI workload resource group."
  value       = azurerm_resource_group.ai_assistant.name
}

output "vnet_id" {
  description = "Resource ID of the DevOnboard AI spoke virtual network."
  value       = module.aiast_vnet.vnet_id
}

output "vnet_name" {
  description = "Name of the DevOnboard AI spoke virtual network."
  value       = module.aiast_vnet.vnet_name
}

output "openai_account_name" {
  description = "Name of the Azure OpenAI account."
  value       = module.openai.name
}

output "openai_endpoint" {
  description = "Endpoint URL for Azure OpenAI."
  value       = module.openai.endpoint
}

output "function_app_name" {
  description = "Name of the serverless Function App."
  value       = module.function_app.name
}

output "function_app_default_hostname" {
  description = "Default hostname of the Function App."
  value       = module.function_app.default_hostname
}

output "function_app_system_identity_principal_id" {
  description = "System-Assigned Managed Identity Principal ID of the Function App."
  value       = module.function_app.principal_id
  sensitive   = true
}

output "app_insights_instrumentation_key" {
  description = "Application Insights Instrumentation Key."
  value       = module.function_app.app_insights_instrumentation_key
  sensitive   = true
}

output "cosmos_db_account_name" {
  description = "Name of the Cosmos DB account."
  value       = module.cosmos_db.name
}

output "cosmos_db_endpoint" {
  description = "Endpoint URL of the Cosmos DB account."
  value       = module.cosmos_db.endpoint
}

output "search_service_name" {
  description = "Name of the Azure AI Search Service."
  value       = module.search_service.name
}

output "search_service_endpoint" {
  description = "Endpoint URL of the Azure AI Search Service."
  value       = module.search_service.endpoint
}

output "static_web_app_name" {
  description = "Name of the Azure Static Web App."
  value       = azurerm_static_web_app.frontend.name
}

output "static_web_app_url" {
  description = "Default hostname for the Static Web App."
  value       = azurerm_static_web_app.frontend.default_host_name
}

output "static_web_app_api_key" {
  description = "Deployment token for Static Web App CI/CD."
  value       = azurerm_static_web_app.frontend.api_key
  sensitive   = true
}



