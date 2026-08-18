# ==============================================================================
# Workload: BankCompliance AI — Security & RBAC Tier
# Purpose: Shared Content Safety RBAC role assignments for Application Pod Identity
# ==============================================================================

# ─── Shared Azure AI Content Safety Lookup & Access ───────────────────────────

data "azurerm_cognitive_account" "content_safety" {
  provider            = azurerm.shared
  name                = var.shared_content_safety_name
  resource_group_name = var.shared_resource_group_name
}

resource "azurerm_role_assignment" "bankc_cs_user" {
  provider             = azurerm.shared
  count                = var.enable_role_assignments ? 1 : 0
  scope                = data.azurerm_cognitive_account.content_safety.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_user_assigned_identity.bankc_app.principal_id

  depends_on = [
    data.azurerm_cognitive_account.content_safety,
    azurerm_user_assigned_identity.bankc_app
  ]
}
