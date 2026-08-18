# ==============================================================================
# Workload: BankCompliance AI — AKS Compute & Workload Identity
# Purpose: Free-tier Kubernetes cluster for LiteLLM, FastAPI, and Qdrant Vector DB
# ==============================================================================

# ─── AKS Managed Cluster ──────────────────────────────────────────────────────

module "bank_compliance_aks" {
  source = "../../modules/aks"

  name                       = module.bankc_aks_name.name
  resource_group_name        = azurerm_resource_group.bank_compliance.name
  location                   = azurerm_resource_group.bank_compliance.location
  dns_prefix                 = "aks-${var.project}-${var.workload}-${var.environment}-${var.location_short}"
  sku_tier                   = var.aks_sku_tier
  subnet_id                  = module.bankc_vnet.subnet_ids[0] # snet-aks
  vnet_id                    = module.bankc_vnet.vnet_id
  enable_role_assignments    = var.enable_role_assignments
  enable_azure_policy        = var.enable_azure_policy
  node_count                 = var.aks_node_count
  vm_size                    = var.aks_vm_size
  os_disk_type               = "Ephemeral"
  os_disk_size_gb            = var.aks_os_disk_size_gb
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id
  tags                       = local.tags

  depends_on = [
    module.bankc_vnet,
    module.spoke_to_hub_peering
  ]
}

# ─── Application Pod Workload Identity (OIDC Federation) ──────────────────────

resource "azurerm_user_assigned_identity" "bankc_app" {
  name                = module.bankc_uami_name.name
  resource_group_name = azurerm_resource_group.bank_compliance.name
  location            = azurerm_resource_group.bank_compliance.location
  tags                = local.tags
}

resource "azurerm_federated_identity_credential" "bankc_app" {
  name                      = "fic-${var.project}-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  audience                  = ["api://AzureADTokenExchange"]
  issuer                    = module.bank_compliance_aks.oidc_issuer_url
  user_assigned_identity_id = azurerm_user_assigned_identity.bankc_app.id
  subject                   = "system:serviceaccount:bank-compliance:bankc-sa"

  depends_on = [
    module.bank_compliance_aks,
    azurerm_user_assigned_identity.bankc_app
  ]
}
