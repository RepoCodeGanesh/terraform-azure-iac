# ==============================================================================
# Module: Azure Kubernetes Service (AKS Free Tier)
# Purpose: AI Microservices Hosting (LiteLLM, Qdrant Vector DB, FastAPI Backend)
# Cost:    $0.00 Control Plane (Free Tier) + B2s / Ephemeral OS nodes + KEDA scale-to-zero
# ==============================================================================

terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

# ─── Control Plane User-Assigned Managed Identity ─────────────────────────────
resource "azurerm_user_assigned_identity" "aks_control_plane" {
  name                = "uami-aks-${var.name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags
}

resource "azurerm_role_assignment" "aks_vnet_contributor" {
  count                = var.enable_role_assignments && var.vnet_id != null ? 1 : 0
  scope                = var.vnet_id
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_user_assigned_identity.aks_control_plane.principal_id
}

# ─── AKS Cluster ──────────────────────────────────────────────────────────────
resource "azurerm_kubernetes_cluster" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  sku_tier            = var.sku_tier

  oidc_issuer_enabled       = true
  workload_identity_enabled = true
  azure_policy_enabled      = var.enable_azure_policy

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aks_control_plane.id]
  }

  default_node_pool {
    name                        = var.node_pool_name
    node_count                  = var.node_count
    vm_size                     = var.vm_size
    os_disk_type                = var.os_disk_type
    os_disk_size_gb             = var.os_disk_size_gb
    vnet_subnet_id              = var.subnet_id
    type                        = "VirtualMachineScaleSets"
    temporary_name_for_rotation = "temppool"
    tags                        = var.tags
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    pod_cidr            = var.pod_cidr
    dns_service_ip      = var.dns_service_ip
    service_cidr        = var.service_cidr
  }

  web_app_routing {
    dns_zone_ids = []
  }

  key_vault_secrets_provider {
    secret_rotation_enabled = true
  }

  workload_autoscaler_profile {
    keda_enabled = true
  }

  dynamic "oms_agent" {
    for_each = var.log_analytics_workspace_id != null ? [1] : []
    content {
      log_analytics_workspace_id      = var.log_analytics_workspace_id
      msi_auth_for_monitoring_enabled = true
    }
  }

  tags = var.tags

  depends_on = [
    azurerm_role_assignment.aks_vnet_contributor
  ]
}

# ─── Diagnostics to Central Log Analytics Workspace ──────────────────────────
resource "azurerm_monitor_diagnostic_setting" "aks_diagnostics" {
  count                      = var.log_analytics_workspace_id != null ? 1 : 0
  name                       = "diag-${var.name}"
  target_resource_id         = azurerm_kubernetes_cluster.this.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "kube-apiserver"
  }

  enabled_log {
    category = "kube-audit-admin"
  }

  enabled_log {
    category = "kube-controller-manager"
  }

  enabled_log {
    category = "cluster-autoscaler"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}
