# ==============================================================================
# Workload: BankCompliance AI — Regulatory Data Lake Storage Account
# Architecture:
#   - Storage Account: sthtbankcpcin01 (Standard LRS, StorageV2, TLS 1.2)
#   - Container:       rbi-raw-pdfs (Houses Master Directions & circulars)
#   - Security:        Passwordless RBAC (Storage Blob Data Contributor)
#                      granted to uami-ht-bankc-p-cin-01 via Workload Identity
# ==============================================================================

module "bankc_storage" {
  source = "../../modules/storage_account"

  name                          = module.naming.names["st"]
  resource_group_name           = azurerm_resource_group.bank_compliance.name
  location                      = var.location
  account_tier                  = "Standard"
  account_replication_type      = "LRS"
  account_kind                  = "StorageV2"
  public_network_access_enabled = true
  shared_access_key_enabled     = true

  container_name        = "rbi-raw-pdfs"
  container_access_type = "private"

  blob_retention_days      = 1
  container_retention_days = 1

  tags = local.tags
}

# ─── RBAC: Grant AKS Workload Identity access to Regulatory Blob Lake ──────────

resource "azurerm_role_assignment" "bankc_storage_blob_contributor" {
  scope                = module.bankc_storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.bankc_app.principal_id
}
