# ==============================================================================
# Workload: BankCompliance AI — Outputs
# Formatted for Kubernetes manifests, GitHub Actions, and DNS configuration
# ==============================================================================

output "resource_group_name" {
  description = "The name of the BankCompliance AI resource group."
  value       = azurerm_resource_group.bank_compliance.name
}

output "vnet_id" {
  description = "The ID of the Spoke Virtual Network."
  value       = module.bankc_vnet.vnet_id
}

output "aks_cluster_id" {
  description = "The ID of the AKS cluster."
  value       = module.bank_compliance_aks.id
}

output "aks_cluster_name" {
  description = "The name of the AKS cluster."
  value       = module.bank_compliance_aks.name
}

output "aks_oidc_issuer_url" {
  description = "The OIDC Issuer URL of the AKS cluster for Workload Identity."
  value       = module.bank_compliance_aks.oidc_issuer_url
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
  value       = module.bankc_frontend.name
}

output "static_web_app_default_host_name" {
  description = "The default URL of the Static Web App (e.g. agreeable-beach-xxx.azurestaticapps.net)."
  value       = module.bankc_frontend.default_host_name
}

output "static_web_app_api_key" {
  description = "Deployment token for the Static Web App."
  value       = module.bankc_frontend.api_key
  sensitive   = true
}

output "key_vault_secret_name" {
  description = "The secret name in central Key Vault for the Static Web App deployment token."
  value       = azurerm_key_vault_secret.bankc_swa_api_token.name
}

output "cloudflare_cname_record_id" {
  description = "The Cloudflare DNS CNAME record ID for bank.mytaxbot.site."
  value       = cloudflare_record.bankc_cname.id
}

output "custom_domain_url" {
  description = "The verified public URL for BankCompliance AI."
  value       = var.custom_domain_name != null ? "https://${var.custom_domain_name}" : "https://${module.bankc_frontend.default_host_name}"
}

output "dns_and_custom_domain_summary" {
  description = "Complete summary of automated DNS and custom domain configuration."
  value       = <<-EOT
    ================================================================================
    🌐 CLOUDFLARE DNS & AZURE CUSTOM DOMAIN AUTOMATION COMPLETE!
    ================================================================================
    • Public App URL:       https://${var.custom_domain_name}
    • DNS CNAME Record:     bank.mytaxbot.site ➔ ${module.bankc_frontend.default_host_name}
    • DNS Automation:       Cloudflare API (Record ID: ${cloudflare_record.bankc_cname.id})
    • SSL Certificate:      Active (Auto-provisioned & Managed by Azure SWA)
    • APIM Gateway URL:     ${startswith(data.azurerm_api_management.shared.gateway_url, "https://") ? "${data.azurerm_api_management.shared.gateway_url}/bankc" : "https://${data.azurerm_api_management.shared.gateway_url}/bankc"}
    ================================================================================
  EOT
}

output "apim_gateway_url" {
  description = "The gateway URL for BankCompliance AI via APIM."
  value       = startswith(data.azurerm_api_management.shared.gateway_url, "https://") ? "${data.azurerm_api_management.shared.gateway_url}/bankc" : "https://${data.azurerm_api_management.shared.gateway_url}/bankc"
}

output "app_insights_name" {
  description = "The name of the dedicated Application Insights instance for BankCompliance."
  value       = module.bank_compliance_appi.name
}

output "app_insights_connection_string" {
  description = "Connection string for Application Insights OpenTelemetry."
  value       = module.bank_compliance_appi.connection_string
  sensitive   = true
}

output "app_insights_instrumentation_key" {
  description = "Instrumentation key for Application Insights."
  value       = module.bank_compliance_appi.instrumentation_key
  sensitive   = true
}
