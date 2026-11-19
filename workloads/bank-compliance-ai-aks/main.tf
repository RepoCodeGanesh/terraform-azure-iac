# ==============================================================================
# Workload: BankCompliance AI — Core & Naming
# Domain:   Banking Regulatory & Master Direction Copilot (RBI Compliance)
# Cost:     $0.00 base control plane (AKS Free Tier + SWA Free + APIM Consumption)
# ==============================================================================

data "azurerm_client_config" "current" {}

# ─── Shared Services Lookups (LAW, APIM, Key Vault) ───────────────────────────

data "azurerm_resource_group" "shared" {
  provider = azurerm.shared
  name     = var.shared_resource_group_name
}

data "azurerm_log_analytics_workspace" "shared" {
  provider            = azurerm.shared
  name                = var.shared_law_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

data "azurerm_api_management" "shared" {
  provider            = azurerm.shared
  name                = var.shared_apim_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

data "azurerm_key_vault" "shared" {
  provider            = azurerm.shared
  name                = var.shared_key_vault_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

data "azurerm_key_vault_secret" "cloudflare_api_token" {
  provider     = azurerm.shared
  name         = "cloudflare-api-token"
  key_vault_id = data.azurerm_key_vault.shared.id
}

# ─── CAF Resource Naming Module (Batch Generation) ───────────────────────────

module "naming" {
  source         = "../../modules/naming"
  resource_types = ["rg", "vnet", "aks", "uami", "stapp", "appi", "st"]
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

# ─── Workload Resource Group ──────────────────────────────────────────────────

resource "azurerm_resource_group" "bank_compliance" {
  name     = module.naming.names["rg"]
  location = var.location
  tags     = local.tags
}

# ─── Workload Application Insights (APM) ──────────────────────────────────────

module "bank_compliance_appi" {
  source = "../../modules/application_insights"

  name                = module.naming.names["appi"]
  location            = var.location
  resource_group_name = azurerm_resource_group.bank_compliance.name
  workspace_id        = data.azurerm_log_analytics_workspace.shared.id
  application_type    = "web"
  tags                = local.tags
}
