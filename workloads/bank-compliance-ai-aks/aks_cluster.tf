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
  enable_web_app_routing     = false # FinOps: Disabled — community Ingress-NGINX at 1m CPU used instead
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

# ─── Secondary Spot Instance Node Pool (FinOps 80%+ Cost Savings) ───────────

resource "azurerm_kubernetes_cluster_node_pool" "spot" {
  count                 = var.enable_spot_node_pool ? 1 : 0
  name                  = "spotpool"
  kubernetes_cluster_id = module.bank_compliance_aks.id
  vm_size               = var.aks_spot_vm_size
  vnet_subnet_id        = module.bankc_vnet.subnet_ids[0] # snet-aks
  os_disk_type          = "Ephemeral"
  os_disk_size_gb       = 30

  # Spot Pricing & Eviction Policy
  priority        = "Spot"
  eviction_policy = "Delete"
  spot_max_price  = -1 # Pay up to on-demand price; prevents eviction by price spikes

  # FinOps Autoscaling (0 to 3 nodes)
  auto_scaling_enabled = true
  min_count            = 0
  max_count            = var.aks_spot_max_count
  node_count           = 0

  node_taints = [
    "kubernetes.azure.com/scalesetpriority=spot:NoSchedule"
  ]

  node_labels = {
    "nodepool"                              = "spot"
    "kubernetes.azure.com/scalesetpriority" = "spot"
  }

  tags = local.tags

  depends_on = [
    module.bank_compliance_aks
  ]
}
