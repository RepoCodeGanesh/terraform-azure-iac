output "resource_group_name" {
  description = "The name of the BankCompliance AI resource group."
  value       = azurerm_resource_group.bank_compliance.name
}

output "vnet_id" {
  description = "The ID of the Spoke Virtual Network."
  value       = azurerm_virtual_network.bank_compliance.id
}

output "aks_cluster_id" {
  description = "The ID of the AKS cluster."
  value       = azurerm_kubernetes_cluster.bank_compliance.id
}

output "aks_cluster_name" {
  description = "The name of the AKS cluster."
  value       = azurerm_kubernetes_cluster.bank_compliance.name
}

output "aks_oidc_issuer_url" {
  description = "The OIDC Issuer URL of the AKS cluster for Workload Identity."
  value       = azurerm_kubernetes_cluster.bank_compliance.oidc_issuer_url
}

output "aks_workload_identity_client_id" {
  description = "Client ID of the User-Assigned Identity used for pod Workload Identity federation."
  value       = azurerm_user_assigned_identity.bankc_app.client_id
}

output "content_safety_id" {
  description = "The ID of the shared Azure AI Content Safety account."
  value       = data.azurerm_cognitive_account.content_safety.id
}

output "content_safety_endpoint" {
  description = "The endpoint of the shared Azure AI Content Safety account."
  value       = data.azurerm_cognitive_account.content_safety.endpoint
}

output "static_web_app_name" {
  description = "The name of the Static Web App frontend."
  value       = azurerm_static_web_app.bankc_frontend.name
}

output "static_web_app_default_host_name" {
  description = "The default URL of the Static Web App (e.g. agreeable-beach-xxx.azurestaticapps.net)."
  value       = azurerm_static_web_app.bankc_frontend.default_host_name
}

output "static_web_app_api_key" {
  description = "Deployment token for the Static Web App."
  value       = azurerm_static_web_app.bankc_frontend.api_key
  sensitive   = true
}

output "key_vault_secret_name" {
  description = "The secret name in central Key Vault for the Static Web App deployment token."
  value       = azurerm_key_vault_secret.bankc_swa_api_token.name
}

output "custom_domain_cname_instruction" {
  description = "Instruction for DNS CNAME configuration at domain registrar."
  value       = "Create a CNAME record at your DNS provider: Host 'bank' pointing to '${azurerm_static_web_app.bankc_frontend.default_host_name}', then set enable_custom_domain = true in prod.tfvars."
}

output "apim_gateway_url" {
  description = "The gateway URL for BankCompliance AI via APIM."
  value       = startswith(data.azurerm_api_management.shared.gateway_url, "https://") ? "${data.azurerm_api_management.shared.gateway_url}/bankc" : "https://${data.azurerm_api_management.shared.gateway_url}/bankc"
}

output "app_insights_name" {
  description = "The name of the dedicated Application Insights instance for BankCompliance."
  value       = azurerm_application_insights.bank_compliance.name
}

output "app_insights_connection_string" {
  description = "Connection string for Application Insights OpenTelemetry."
  value       = azurerm_application_insights.bank_compliance.connection_string
  sensitive   = true
}

output "app_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights."
  value       = azurerm_application_insights.bank_compliance.instrumentation_key
  sensitive   = true
}

