# ==============================================================================
# Workload: BankCompliance AI — Security & RBAC Tier
# Purpose: Shared Content Safety Lookups for Application Pod Identity
# ==============================================================================

# ─── Shared Azure AI Content Safety Lookup & Access ───────────────────────────

data "azurerm_cognitive_account" "content_safety" {
  provider            = azurerm.shared
  name                = var.shared_content_safety_name
  resource_group_name = var.shared_resource_group_name
}

# ─── State Migration: Cleanly forget legacy cross-sub role assignment ─────────
# Role assignments on shared services resources are governed by platform/shared-services.
# Removing from state without calling Azure IAM DELETE API to prevent 403 Forbidden.

removed {
  from = azurerm_role_assignment.bankc_cs_user

  lifecycle {
    destroy = false
  }
}
