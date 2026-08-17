data "azurerm_client_config" "current" {}

# Lookups for Hub VNet (for peering)
data "azurerm_resource_group" "hub" {
  provider = azurerm.hub
  name     = var.hub_resource_group_name
}

data "azurerm_virtual_network" "hub" {
  provider            = azurerm.hub
  name                = var.hub_vnet_name
  resource_group_name = data.azurerm_resource_group.hub.name
}

# Lookups for Shared Services Resources (LAW, APIM)
data "azurerm_resource_group" "shared" {
  provider = azurerm.shared
  name     = var.shared_resource_group_name
}

data "azurerm_log_analytics_workspace" "shared" {
  provider            = azurerm.shared
  name                = var.shared_law_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

data "azurerm_api_management" "shared" {
  provider            = azurerm.shared
  name                = var.shared_apim_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

data "azurerm_key_vault" "shared" {
  provider            = azurerm.shared
  name                = var.shared_key_vault_name
  resource_group_name = data.azurerm_resource_group.shared.name
}

# ─── Naming Modules ───────────────────────────────────────────────────────────

module "bankc_rg_name" {
  source         = "../../modules/naming"
  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "bankc_vnet_name" {
  source         = "../../modules/naming"
  resource_type  = "vnet"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "bankc_aks_name" {
  source         = "../../modules/naming"
  resource_type  = "aks"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

# bankc_cs_name removed — Content Safety is now shared via platform/shared-services

module "bankc_uami_name" {
  source         = "../../modules/naming"
  resource_type  = "uami"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "bankc_stapp_name" {
  source         = "../../modules/naming"
  resource_type  = "stapp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "bankc_appi_name" {
  source         = "../../modules/naming"
  resource_type  = "appi"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

# ─── Resource Group ───────────────────────────────────────────────────────────

resource "azurerm_resource_group" "bank_compliance" {
  name     = module.bankc_rg_name.name
  location = var.location
  tags     = local.tags
}

# ─── Application Performance Monitoring (Application Insights) ────────────────

resource "azurerm_application_insights" "bank_compliance" {
  name                = module.bankc_appi_name.name
  location            = var.location
  resource_group_name = azurerm_resource_group.bank_compliance.name
  workspace_id        = data.azurerm_log_analytics_workspace.shared.id
  application_type    = "web"
  tags                = local.tags
}


# ─── Spoke Virtual Network & Subnets ──────────────────────────────────────────

resource "azurerm_virtual_network" "bank_compliance" {
  name                = module.bankc_vnet_name.name
  location            = azurerm_resource_group.bank_compliance.location
  resource_group_name = azurerm_resource_group.bank_compliance.name
  address_space       = var.vnet_address_space
  tags                = local.tags
}

resource "azurerm_subnet" "aks" {
  name                 = "snet-aks-${var.project}-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  resource_group_name  = azurerm_resource_group.bank_compliance.name
  virtual_network_name = azurerm_virtual_network.bank_compliance.name
  address_prefixes     = [var.aks_subnet_prefix]
}

resource "azurerm_subnet" "private_endpoints" {
  name                 = "snet-pe-${var.project}-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  resource_group_name  = azurerm_resource_group.bank_compliance.name
  virtual_network_name = azurerm_virtual_network.bank_compliance.name
  address_prefixes     = [var.private_endpoints_subnet_prefix]
}

# ─── Bi-directional VNet Peering to Hub ───────────────────────────────────────

module "spoke_to_hub_peering" {
  source = "../../modules/vnet_peering"

  providers = {
    azurerm.vnet_1 = azurerm
    azurerm.vnet_2 = azurerm.hub
  }

  vnet_1_name = azurerm_virtual_network.bank_compliance.name
  vnet_1_rg   = azurerm_resource_group.bank_compliance.name
  vnet_1_id   = azurerm_virtual_network.bank_compliance.id

  vnet_2_name = data.azurerm_virtual_network.hub.name
  vnet_2_rg   = data.azurerm_resource_group.hub.name
  vnet_2_id   = data.azurerm_virtual_network.hub.id

  depends_on = [
    azurerm_virtual_network.bank_compliance
  ]
}

# ─── User-Assigned Managed Identities ─────────────────────────────────────────

# Identity used by the AKS Control Plane to manage Spoke VNet networking
resource "azurerm_user_assigned_identity" "aks_control_plane" {
  name                = "uami-aks-${var.project}-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  resource_group_name = azurerm_resource_group.bank_compliance.name
  location            = azurerm_resource_group.bank_compliance.location
  tags                = local.tags
}

resource "azurerm_role_assignment" "aks_vnet_contributor" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = azurerm_virtual_network.bank_compliance.id
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_user_assigned_identity.aks_control_plane.principal_id
}

# Identity used by the BankCompliance application pods via Workload Identity (OIDC)
resource "azurerm_user_assigned_identity" "bankc_app" {
  name                = module.bankc_uami_name.name
  resource_group_name = azurerm_resource_group.bank_compliance.name
  location            = azurerm_resource_group.bank_compliance.location
  tags                = local.tags
}

# ─── Azure Kubernetes Service (AKS Free Tier) ─────────────────────────────────

resource "azurerm_kubernetes_cluster" "bank_compliance" {
  name                = module.bankc_aks_name.name
  location            = azurerm_resource_group.bank_compliance.location
  resource_group_name = azurerm_resource_group.bank_compliance.name
  dns_prefix          = "aks-${var.project}-${var.workload}-${var.environment}-${var.location_short}"
  sku_tier            = var.aks_sku_tier

  oidc_issuer_enabled       = true
  workload_identity_enabled = true
  azure_policy_enabled      = var.enable_azure_policy

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aks_control_plane.id]
  }

  default_node_pool {
    name                        = "system"
    node_count                  = var.aks_node_count
    vm_size                     = var.aks_vm_size
    os_disk_type                = "Ephemeral"
    os_disk_size_gb             = var.aks_os_disk_size_gb
    vnet_subnet_id              = azurerm_subnet.aks.id
    type                        = "VirtualMachineScaleSets"
    temporary_name_for_rotation = "temppool"
    tags                        = local.tags
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    pod_cidr            = "10.244.0.0/16"
    dns_service_ip      = "172.16.0.10"
    service_cidr        = "172.16.0.0/16"
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

  oms_agent {
    log_analytics_workspace_id      = data.azurerm_log_analytics_workspace.shared.id
    msi_auth_for_monitoring_enabled = true
  }

  tags = local.tags

  depends_on = [
    azurerm_role_assignment.aks_vnet_contributor
  ]
}

# ─── AKS Diagnostic Settings to Central Log Analytics ─────────────────────────

resource "azurerm_monitor_diagnostic_setting" "aks_diagnostics" {
  name                       = "diag-${module.bankc_aks_name.name}"
  target_resource_id         = azurerm_kubernetes_cluster.bank_compliance.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

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

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# ─── Workload Identity Federated Credential ───────────────────────────────────

resource "azurerm_federated_identity_credential" "bankc_app" {
  name                      = "fic-${var.project}-${var.workload}-${var.environment}-${var.location_short}-${var.instance}"
  audience                  = ["api://AzureADTokenExchange"]
  issuer                    = azurerm_kubernetes_cluster.bank_compliance.oidc_issuer_url
  user_assigned_identity_id = azurerm_user_assigned_identity.bankc_app.id
  subject                   = "system:serviceaccount:bank-compliance:bankc-sa"

  depends_on = [
    azurerm_kubernetes_cluster.bank_compliance,
    azurerm_user_assigned_identity.bankc_app
  ]
}

# ─── Shared Azure AI Content Safety (from platform/shared-services) ─────────────────
data "azurerm_cognitive_account" "content_safety" {
  provider            = azurerm.shared
  name                = var.shared_content_safety_name
  resource_group_name = var.shared_resource_group_name
}

resource "azurerm_role_assignment" "bankc_cs_user" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = data.azurerm_cognitive_account.content_safety.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_user_assigned_identity.bankc_app.principal_id

  depends_on = [
    data.azurerm_cognitive_account.content_safety,
    azurerm_user_assigned_identity.bankc_app
  ]
}

# ─── Azure Static Web App (Frontend on bank.mytaxbot.site) ────────────────────

resource "azurerm_static_web_app" "bankc_frontend" {
  name                = module.bankc_stapp_name.name
  resource_group_name = azurerm_resource_group.bank_compliance.name
  location            = var.swa_location
  sku_tier            = "Free"
  sku_size            = "Free"
  tags                = local.tags
}

resource "azurerm_static_web_app_custom_domain" "bankc" {
  count             = var.enable_custom_domain ? 1 : 0
  static_web_app_id = azurerm_static_web_app.bankc_frontend.id
  domain_name       = var.custom_domain_name
  validation_type   = "cname-delegation"

  depends_on = [
    azurerm_static_web_app.bankc_frontend
  ]
}

# ─── SWA Deployment Token stored in Central Key Vault ─────────────────────────

resource "azurerm_key_vault_secret" "bankc_swa_api_token" {
  provider     = azurerm.shared
  name         = "bankc-swa-deployment-token"
  value        = azurerm_static_web_app.bankc_frontend.api_key
  key_vault_id = data.azurerm_key_vault.shared.id
  tags         = local.tags

  depends_on = [
    azurerm_static_web_app.bankc_frontend,
    data.azurerm_key_vault.shared
  ]
}

# ─── APIM Backend for BankCompliance AKS ──────────────────────────────────────

resource "azurerm_api_management_backend" "bankc_backend" {
  provider            = azurerm.shared
  name                = "aks-backend-${var.workload}"
  resource_group_name = data.azurerm_resource_group.shared.name
  api_management_name = data.azurerm_api_management.shared.name
  protocol            = "http"
  url                 = "http://bankc-api-ht-cin.centralindia.cloudapp.azure.com"
  description         = "APIM backend for BankCompliance AKS backend"
}

# ─── APIM API Definition for BankCompliance AI ────────────────────────────────

resource "azapi_resource" "apim_bankc_api" {
  type      = "Microsoft.ApiManagement/service/apis@2022-08-01"
  name      = "bankc-compliance-api"
  parent_id = data.azurerm_api_management.shared.id

  body = {
    properties = {
      displayName          = "BankCompliance AI — Regulatory Copilot"
      path                 = "bankc"
      protocols            = ["https"]
      serviceUrl           = "http://bankc-api-ht-cin.centralindia.cloudapp.azure.com"
      subscriptionRequired = false
    }
  }

  depends_on = [azurerm_api_management_backend.bankc_backend]
}

# POST /api/v1/compliance/query
resource "azapi_resource" "compliance_query_post" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "compliance-query-post"
  parent_id = azapi_resource.apim_bankc_api.id

  body = {
    properties = {
      displayName = "Query Compliance"
      method      = "POST"
      urlTemplate = "/api/v1/compliance/query"
      description = "Submit regulatory compliance question"
    }
  }

  depends_on = [azapi_resource.apim_bankc_api]
}

# GET /healthz
resource "azapi_resource" "bankc_healthz_get" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "healthz-get"
  parent_id = azapi_resource.apim_bankc_api.id

  body = {
    properties = {
      displayName = "Health Check"
      method      = "GET"
      urlTemplate = "/healthz"
      description = "Returns AKS backend health status"
    }
  }

  depends_on = [azapi_resource.apim_bankc_api]
}

# GET /api/v1/compliance/circulars
resource "azapi_resource" "compliance_circulars_get" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "compliance-circulars-get"
  parent_id = azapi_resource.apim_bankc_api.id

  body = {
    properties = {
      displayName = "List Master Directions"
      method      = "GET"
      urlTemplate = "/api/v1/compliance/circulars"
      description = "Returns list of indexed RBI circulars"
    }
  }

  depends_on = [azapi_resource.apim_bankc_api]
}

# ─── APIM Policy: CORS + Forward to AKS Backend ────────────────────────────────

resource "azapi_resource" "bankc_cors_policy" {
  type      = "Microsoft.ApiManagement/service/apis/policies@2022-08-01"
  name      = "policy"
  parent_id = azapi_resource.apim_bankc_api.id

  body = {
    properties = {
      format = "xml"
      value  = <<XML
<policies>
  <inbound>
    <cors allow-credentials="false">
      <allowed-origins>
        <origin>*</origin>
      </allowed-origins>
      <allowed-methods preflight-result-max-age="300">
        <method>POST</method>
        <method>GET</method>
        <method>OPTIONS</method>
      </allowed-methods>
      <allowed-headers>
        <header>*</header>
      </allowed-headers>
    </cors>
    <set-backend-service backend-id="aks-backend-${var.workload}" />
  </inbound>
  <backend>
    <forward-request timeout="30" />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
XML
    }
  }

  depends_on = [azapi_resource.apim_bankc_api]
}

