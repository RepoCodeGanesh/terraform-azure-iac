# ==============================================================================
# Workload: TaxBot India — AI & Data Tier
# Purpose: Shared OpenAI & Content Safety lookups, Cosmos DB session history, AI Search RAG index
# Cost:    $0.00 base cost (Cosmos DB 400 RU/s Free Tier + AI Search Free Tier)
# ==============================================================================

# ─── Shared Azure OpenAI (from platform/shared-services) ──────────────────────

data "azurerm_cognitive_account" "openai" {
  provider            = azurerm.shared
  name                = var.shared_openai_name
  resource_group_name = var.shared_resource_group_name
}

# ─── Shared Azure AI Content Safety (from platform/shared-services) ───────────

data "azurerm_cognitive_account" "content_safety" {
  provider            = azurerm.shared
  name                = var.shared_content_safety_name
  resource_group_name = var.shared_resource_group_name
}

# ─── Cosmos DB (Free Tier — session history for TaxBot chat) ──────────────────

module "cosmos_db" {
  source = "../../modules/cosmos_db"

  name                = module.taxb_cosmos_name.name
  location            = azurerm_resource_group.tax_advisor.location
  resource_group_name = azurerm_resource_group.tax_advisor.name
  enable_free_tier    = true
  database_name       = "db-tax-advisor"
  container_name      = "chat_history"

  tags = local.tags
}

# ─── Azure AI Search (Free tier — tax document RAG index) ─────────────────────

module "search_service" {
  source = "../../modules/search_service"

  name                = module.taxb_srch_name.name
  location            = azurerm_resource_group.tax_advisor.location
  resource_group_name = azurerm_resource_group.tax_advisor.name
  sku                 = "free"

  tags = local.tags
}
