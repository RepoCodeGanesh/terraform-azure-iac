# ==============================================================================
# Platform: Shared Services — Security & Key Vault
# Purpose: Central platform Key Vault with RBAC Authorization
# Cost:    Standard Key Vault ($0 base cost, ~$0.03/10k transactions)
# ==============================================================================

# ─── Central Key Vault ────────────────────────────────────────────────────────

module "shared_key_vault" {
  source = "../../modules/key_vault"

  name                          = module.shared_kv_name.name
  resource_group_name           = azurerm_resource_group.shared_services.name
  location                      = azurerm_resource_group.shared_services.location
  tenant_id                     = data.azurerm_client_config.current.tenant_id
  sku_name                      = "standard"
  enable_rbac_authorization     = true
  public_network_access_enabled = true
  purge_protection_enabled      = false
  soft_delete_retention_days    = 7
  tags                          = local.tags
}

# ─── Workload RBAC: App-Prod Service Principal Access ────────────────────────
# The bank-compliance workload writes bankc-swa-deployment-token into this vault
# via provider = azurerm.shared. The app-prod SP needs Key Vault Secrets Officer.

resource "azurerm_role_assignment" "app_prod_kv_secrets_officer" {
  scope                = module.shared_key_vault.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = var.app_prod_sp_object_id

  depends_on = [module.shared_key_vault]
}

# ─── Workload RBAC: App-Prod SP Role Delegation on Shared Content Safety ─────
# Grants the app-prod SP authority to assign/unassign Cognitive Services User
# roles on the shared Content Safety account for newly created spoke identities.

resource "azurerm_role_assignment" "app_prod_cs_rbac_admin" {
  scope                = module.shared_content_safety.id
  role_definition_name = "Role Based Access Control Administrator"
  principal_id         = var.app_prod_sp_object_id

  depends_on = [module.shared_content_safety]
}

# ─── Workload RBAC: App-Prod SP Role Delegation on Shared OpenAI ─────────────
# Grants the app-prod SP authority to assign/unassign Cognitive Services OpenAI User
# roles on the shared OpenAI account for newly created spoke identities.

resource "azurerm_role_assignment" "app_prod_openai_rbac_admin" {
  scope                = module.shared_openai.id
  role_definition_name = "Role Based Access Control Administrator"
  principal_id         = var.app_prod_sp_object_id

  depends_on = [module.shared_openai]
}

# ─── Workload RBAC: App-Prod SP Contributor on Shared Services Resource Group ─
# Allows app-prod SP to manage APIM APIs, backend mappings, and policies.

resource "azurerm_role_assignment" "app_prod_rg_contributor" {
  scope                = azurerm_resource_group.shared_services.id
  role_definition_name = "Contributor"
  principal_id         = var.app_prod_sp_object_id

  depends_on = [azurerm_resource_group.shared_services]
}

# ─── Platform Registry: Shared AI Endpoints & Keys in Central Key Vault ──────

data "azurerm_cognitive_account" "shared_openai" {
  name                = module.shared_openai.name
  resource_group_name = azurerm_resource_group.shared_services.name

  depends_on = [module.shared_openai]
}

resource "azurerm_key_vault_secret" "openai_endpoint" {
  name         = "openai-endpoint"
  value        = module.shared_openai.endpoint
  key_vault_id = module.shared_key_vault.id
  tags         = local.tags

  depends_on = [module.shared_key_vault, module.shared_openai]
}

resource "azurerm_key_vault_secret" "openai_api_key" {
  name         = "openai-api-key"
  value        = data.azurerm_cognitive_account.shared_openai.primary_access_key
  key_vault_id = module.shared_key_vault.id
  tags         = local.tags

  depends_on = [module.shared_key_vault, data.azurerm_cognitive_account.shared_openai]
}

resource "azurerm_key_vault_secret" "content_safety_endpoint" {
  name         = "content-safety-endpoint"
  value        = module.shared_content_safety.endpoint
  key_vault_id = module.shared_key_vault.id
  tags         = local.tags

  depends_on = [module.shared_key_vault, module.shared_content_safety]
}
