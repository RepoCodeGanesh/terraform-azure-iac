# ==============================================================================
# Workload: TaxBot India — Compute Tier
# Purpose: Serverless Linux Function App (Python 3.11) & Y1 Consumption Plan
# Cost:    $0.00 base cost (Y1 Plan — 1 million free executions / month)
# ==============================================================================

# ─── App Service Plan (Y1 Consumption — $0 idle) ──────────────────────────────

module "taxb_service_plan" {
  source = "../../modules/service_plan"

  name                = module.taxb_asp_name.name
  location            = azurerm_resource_group.tax_advisor.location
  resource_group_name = azurerm_resource_group.tax_advisor.name
  os_type             = "Linux"
  sku_name            = "Y1"
  tags                = local.tags
}

# ─── Function App (Python 3.11 RAG API) ───────────────────────────────────────

module "function_app" {
  source = "../../modules/function_app"

  name                       = module.taxb_func_name.name
  location                   = azurerm_resource_group.tax_advisor.location
  resource_group_id          = azurerm_resource_group.tax_advisor.id
  resource_group_name        = azurerm_resource_group.tax_advisor.name
  storage_account_name       = module.taxb_st_name.name
  service_plan_id            = module.taxb_service_plan.id
  app_insights_name          = module.taxb_appi_name.name
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id
  python_version             = "3.11"
  identity_type              = "SystemAssigned"

  app_settings = {
    "AZURE_OPENAI_ENDPOINT"         = data.azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_MODEL"            = var.openai_model_name
    "COSMOS_DB_ENDPOINT"            = module.cosmos_db.endpoint
    "COSMOS_DB_DATABASE"            = module.cosmos_db.database_name
    "COSMOS_DB_CONTAINER"           = module.cosmos_db.container_name
    "AZURE_SEARCH_ENDPOINT"         = module.search_service.endpoint
    "AZURE_SEARCH_INDEX"            = "tax-docs"
    "AZURE_CONTENT_SAFETY_ENDPOINT" = data.azurerm_cognitive_account.content_safety.endpoint
    "RAG_DOCUMENTS_CONTAINER"       = "documents"
    "APP_NAME"                      = "TaxBot India"
    "APP_VERSION"                   = "1.0.0"
  }

  tags = local.tags
}

# ─── Storage Container for RAG Documents ──────────────────────────────────────

resource "azurerm_storage_container" "rag_documents" {
  name                  = "documents"
  storage_account_id    = module.function_app.storage_account_id
  container_access_type = "private"

  depends_on = [module.function_app]
}

# ─── Function App Identity Data Source (Prevents RBAC Replacement Drift) ──────

data "azurerm_linux_function_app" "taxb_func" {
  name                = module.taxb_func_name.name
  resource_group_name = azurerm_resource_group.tax_advisor.name
  depends_on          = [module.function_app]
}

# ─── Identity Propagation Sleep ────────────────────────────────────────────────

resource "time_sleep" "wait_for_func_identity" {
  create_duration = "10s"
  depends_on      = [module.function_app]
}
