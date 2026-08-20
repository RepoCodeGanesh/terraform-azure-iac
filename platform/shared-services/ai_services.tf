# ==============================================================================
# Platform: Shared Services — Shared AI Platform Services
# Purpose: Shared Azure AI Content Safety (F0) and Azure OpenAI (S0)
# Cost:    Content Safety F0 ($0.00 / 5k calls free) + OpenAI (Pay per token consumed)
# ==============================================================================

# ─── Shared Azure AI Content Safety (F0 Free Tier) ────────────────────────────
# Single shared account consumed by all workloads via data source lookup.
# Lives in the shared-services sub (859a785c) — separate F0 quota from Apps-prod.

module "shared_content_safety" {
  source = "../../modules/content_safety"

  name                = module.shared_cs_name.name
  location            = var.content_safety_location
  resource_group_name = azurerm_resource_group.shared_services.name
  sku_name            = "F0"
  tags                = local.tags

  depends_on = [azurerm_resource_group.shared_services]
}

# ─── Shared Azure OpenAI (S0) ─────────────────────────────────────────────────
# CAF rule: shared AI platform services belong in shared-services sub.
# Both TaxBot (Function App) and BankCompliance (LiteLLM proxy) consume this endpoint.

module "shared_openai" {
  source = "../../modules/cognitive_account"

  name                       = module.shared_oai_name.name
  location                   = var.openai_location
  resource_group_id          = azurerm_resource_group.shared_services.id
  sku_name                   = "S0"
  custom_subdomain_name      = module.shared_oai_name.name
  log_analytics_workspace_id = module.shared_log_analytics.id

  deployments = {
    (var.openai_model_name) = {
      model_format  = "OpenAI"
      model_name    = var.openai_model_name
      model_version = var.openai_model_version
      sku_name      = "GlobalStandard"
      sku_capacity  = var.openai_model_capacity
    }
  }

  tags = local.tags

  depends_on = [azurerm_resource_group.shared_services, module.shared_log_analytics]
}
