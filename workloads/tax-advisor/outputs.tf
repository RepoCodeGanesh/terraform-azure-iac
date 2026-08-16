# ==============================================================================
# Workload: TaxBot India Outputs
# Formatted for immediate usability in CI/CD pipelines, CLI, & developer tooling
# ==============================================================================

output "resource_group_name" {
  description = "Name of the TaxBot India workload resource group."
  value       = azurerm_resource_group.tax_advisor.name
}

output "vnet_id" {
  description = "Resource ID of the TaxBot India spoke virtual network."
  value       = module.taxb_vnet.vnet_id
}

output "vnet_name" {
  description = "Name of the TaxBot India spoke virtual network."
  value       = module.taxb_vnet.vnet_name
}

output "openai_account_name" {
  description = "Name of the shared Azure OpenAI account."
  value       = data.azurerm_cognitive_account.openai.name
}

output "openai_endpoint" {
  description = "Endpoint URL for the shared Azure OpenAI account."
  value       = data.azurerm_cognitive_account.openai.endpoint
}

output "function_app_name" {
  description = "Name of the TaxBot India Function App."
  value       = module.function_app.name
}

output "function_app_default_hostname" {
  description = "Default hostname of the Function App."
  value       = "https://${module.function_app.default_hostname}"
}

output "function_app_system_identity_principal_id" {
  description = "System-Assigned Managed Identity Principal ID (used for RBAC assignments)."
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
  description = "Name of the Azure AI Search service."
  value       = module.search_service.name
}

output "search_service_endpoint" {
  description = "Endpoint URL of the Azure AI Search service."
  value       = module.search_service.endpoint
}

output "static_web_app_name" {
  description = "Name of the Azure Static Web App."
  value       = azurerm_static_web_app.frontend.name
}

output "static_web_app_url" {
  description = "Default clickable URL for the Static Web App."
  value       = "https://${azurerm_static_web_app.frontend.default_host_name}"
}

output "custom_domain_url" {
  description = "Live Production Custom Domain URL for TaxBot India."
  value       = "https://www.mytaxbot.site"
}

output "static_web_app_api_key" {
  description = "Deployment token for the Static Web App."
  value       = azurerm_static_web_app.frontend.api_key
  sensitive   = true
}

output "key_vault_secret_name" {
  description = "The secret name in central Key Vault for the Static Web App deployment token."
  value       = azurerm_key_vault_secret.taxb_swa_api_token.name
}

output "apim_base_url" {
  description = "APIM gateway base URL for TaxBot India API."
  value       = startswith(data.azurerm_api_management.shared.gateway_url, "https://") ? "${data.azurerm_api_management.shared.gateway_url}/tax-advisor" : "https://${data.azurerm_api_management.shared.gateway_url}/tax-advisor"
}
