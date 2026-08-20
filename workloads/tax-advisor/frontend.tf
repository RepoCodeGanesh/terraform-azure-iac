# ==============================================================================
# Workload: TaxBot India — Frontend Hosting Tier
# Purpose: Static Web App for React frontend (www.mytaxbot.site) & Central Key Vault Deployment Token
# Cost:    $0.00 / Month (Static Web App Free Tier)
# ==============================================================================

# ─── Static Web App (Free Tier) ────────────────────────────────────────────────

module "taxb_frontend" {
  source = "../../modules/static_web_app"

  name                = module.taxb_stapp_name.name
  resource_group_name = azurerm_resource_group.tax_advisor.name
  location            = var.swa_location
  sku_tier            = "Free"
  sku_size            = "Free"

  app_settings = {
    "APPINSIGHTS_INSTRUMENTATIONKEY"        = module.function_app.app_insights_instrumentation_key
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = module.function_app.app_insights_connection_string
  }

  tags = local.tags
}

# ─── SWA Deployment Token Stored in Central Key Vault ─────────────────────────

resource "azurerm_key_vault_secret" "taxb_swa_api_token" {
  provider     = azurerm.shared
  name         = "taxb-swa-deployment-token"
  value        = module.taxb_frontend.api_key
  key_vault_id = data.azurerm_key_vault.shared.id
  tags         = local.tags

  depends_on = [
    module.taxb_frontend,
    data.azurerm_key_vault.shared
  ]
}
