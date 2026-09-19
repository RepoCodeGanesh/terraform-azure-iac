# ==============================================================================
# Workload: TaxBot India — Security & RBAC Tier
# Purpose: Least-Privilege Entra ID Role Assignments for Function App Managed Identity
# ==============================================================================

# ─── RBAC: Storage Blob Data Contributor (for RAG Document Ingestion) ─────────

resource "azurerm_role_assignment" "func_blob_contributor" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.function_app.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity]
}

resource "azurerm_role_assignment" "cicd_blob_contributor" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.function_app.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.app_prod_sp_object_id
  depends_on           = [module.function_app]
}

# ─── RBAC: Cognitive Services OpenAI User (for Chat Completions) ──────────────

resource "azurerm_role_assignment" "func_openai_user" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = data.azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, data.azurerm_cognitive_account.openai]
}

# ─── RBAC: Search Index Data Reader (for Vector & Semantic RAG Search) ────────

resource "azurerm_role_assignment" "func_search_reader" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.search_service.id
  role_definition_name = "Search Index Data Reader"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, module.search_service]
}

# ─── RBAC: Cosmos DB SQL Role (for Session & Conversation History) ────────────

resource "azurerm_cosmosdb_sql_role_assignment" "func_cosmos_contributor" {
  count               = var.enable_role_assignments ? 1 : 0
  resource_group_name = azurerm_resource_group.tax_advisor.name
  account_name        = module.cosmos_db.name
  role_definition_id  = "${module.cosmos_db.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  principal_id        = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  scope               = module.cosmos_db.id
  depends_on          = [time_sleep.wait_for_func_identity, module.cosmos_db]
}

# ─── RBAC: Cognitive Services User (for Content Safety Prompt Shield) ──────────

resource "azurerm_role_assignment" "func_content_safety_user" {
  provider             = azurerm.shared
  count                = var.enable_role_assignments ? 1 : 0
  scope                = data.azurerm_cognitive_account.content_safety.id
  role_definition_name = "Cognitive Services User"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, data.azurerm_cognitive_account.content_safety]
}
