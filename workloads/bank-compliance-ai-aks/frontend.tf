# ==============================================================================
# Workload: BankCompliance AI — Frontend Hosting Tier
# Purpose: Azure Static Web App for React SPA & Central Key Vault Deployment Token
# Cost:    $0.00 / Month (Static Web App Free Tier)
# ==============================================================================

# ─── Azure Static Web App (Frontend UI on bank.mytaxbot.site) ─────────────────

module "bankc_frontend" {
  source = "../../modules/static_web_app"

  name                = module.bankc_stapp_name.name
  resource_group_name = azurerm_resource_group.bank_compliance.name
  location            = var.swa_location
  sku_tier            = "Free"
  sku_size            = "Free"
  custom_domain_name  = null # Managed in dns_cloudflare.tf with automated Cloudflare DNS dependency
  tags                = local.tags
}

# ─── SWA Deployment Token Stored in Central Key Vault ─────────────────────────

resource "azurerm_key_vault_secret" "bankc_swa_api_token" {
  provider     = azurerm.shared
  name         = "bankc-swa-deployment-token"
  value        = module.bankc_frontend.api_key
  key_vault_id = data.azurerm_key_vault.shared.id
  tags         = local.tags

  depends_on = [
    module.bankc_frontend,
    data.azurerm_key_vault.shared
  ]
}
