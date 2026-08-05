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

# ─── Naming modules ────────────────────────────────────────────────────────────
module "taxb_rg_name" {
  source         = "../../modules/naming"
  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_vnet_name" {
  source         = "../../modules/naming"
  resource_type  = "vnet"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_oai_name" {
  source         = "../../modules/naming"
  resource_type  = "oai"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.openai_location_short
  instance       = var.instance
}

module "taxb_asp_name" {
  source         = "../../modules/naming"
  resource_type  = "asp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_st_name" {
  source         = "../../modules/naming"
  resource_type  = "st"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_func_name" {
  source         = "../../modules/naming"
  resource_type  = "func"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_appi_name" {
  source         = "../../modules/naming"
  resource_type  = "appi"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_cosmos_name" {
  source         = "../../modules/naming"
  resource_type  = "cosmos"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_srch_name" {
  source         = "../../modules/naming"
  resource_type  = "srch"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "taxb_stapp_name" {
  source         = "../../modules/naming"
  resource_type  = "stapp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

# ─── Resource Group ────────────────────────────────────────────────────────────
resource "azurerm_resource_group" "tax_advisor" {
  name     = module.taxb_rg_name.name
  location = var.location
  tags     = local.tags
}

# ─── Spoke Virtual Network ─────────────────────────────────────────────────────
module "taxb_vnet" {
  source = "../../modules/network"

  resource_group_name = azurerm_resource_group.tax_advisor.name
  location            = azurerm_resource_group.tax_advisor.location
  vnet_name           = module.taxb_vnet_name.name
  address_space       = var.vnet_address_space

  subnet_names = [
    "snet-app-integration",
    "PrivateEndpoints"
  ]

  subnet_prefixes = [
    var.app_subnet_prefix,
    var.private_endpoints_subnet_prefix
  ]

  tags = local.tags
}

# ─── VNet Peering to Hub ───────────────────────────────────────────────────────
module "taxb_to_hub_peering" {
  source = "../../modules/vnet_peering"

  providers = {
    azurerm.vnet_1 = azurerm
    azurerm.vnet_2 = azurerm.hub
  }

  vnet_1_name = module.taxb_vnet.vnet_name
  vnet_1_rg   = azurerm_resource_group.tax_advisor.name
  vnet_1_id   = module.taxb_vnet.vnet_id

  vnet_2_name = data.azurerm_virtual_network.hub.name
  vnet_2_rg   = data.azurerm_resource_group.hub.name
  vnet_2_id   = data.azurerm_virtual_network.hub.id

  depends_on = [module.taxb_vnet]
}

# ─── Azure OpenAI ──────────────────────────────────────────────────────────────
module "openai" {
  source = "../../modules/cognitive_account"

  name                       = module.taxb_oai_name.name
  location                   = var.openai_location
  resource_group_id          = azurerm_resource_group.tax_advisor.id
  sku_name                   = "S0"
  custom_subdomain_name      = module.taxb_oai_name.name
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  deployments = {
    (var.openai_model_name) = {
      model_format  = "OpenAI"
      model_name    = var.openai_model_name
      model_version = var.openai_model_version
      sku_name      = "GlobalStandard"
      sku_capacity  = 10
    }
  }

  tags = local.tags
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

# Data lookup for shared Free AI Search service (1 free search service allowed per subscription)
data "azurerm_search_service" "shared" {
  name                = "srch-ht-dvob-p-cin-01"
  resource_group_name = "rg-ht-dvob-p-cin-01"
}

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

# ─── Function App ──────────────────────────────────────────────────────────────
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
    "AZURE_OPENAI_ENDPOINT"   = module.openai.endpoint
    "AZURE_OPENAI_MODEL"      = var.openai_model_name
    "COSMOS_DB_ENDPOINT"      = module.cosmos_db.endpoint
    "COSMOS_DB_DATABASE"      = module.cosmos_db.database_name
    "COSMOS_DB_CONTAINER"     = module.cosmos_db.container_name
    "AZURE_SEARCH_ENDPOINT"   = "https://${data.azurerm_search_service.shared.name}.search.windows.net"
    "AZURE_SEARCH_INDEX"      = "tax-docs"
    "RAG_DOCUMENTS_CONTAINER" = "documents"
    "APP_NAME"                = "TaxBot India"
    "APP_VERSION"             = "1.0.0"
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

# ─── Identity propagation wait ─────────────────────────────────────────────────
resource "time_sleep" "wait_for_func_identity" {
  create_duration = "10s"
  depends_on      = [module.function_app]
}

# ─── RBAC Role Assignments ─────────────────────────────────────────────────────
resource "azurerm_role_assignment" "func_blob_contributor" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.function_app.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.function_app.principal_id
  depends_on           = [time_sleep.wait_for_func_identity]
}

resource "azurerm_role_assignment" "func_openai_user" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.function_app.principal_id
  depends_on           = [time_sleep.wait_for_func_identity, module.openai]
}

resource "azurerm_role_assignment" "func_search_reader" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = data.azurerm_search_service.shared.id
  role_definition_name = "Search Index Data Reader"
  principal_id         = module.function_app.principal_id
  depends_on           = [time_sleep.wait_for_func_identity]
}

resource "azurerm_cosmosdb_sql_role_assignment" "func_cosmos_contributor" {
  count               = var.enable_role_assignments ? 1 : 0
  resource_group_name = azurerm_resource_group.tax_advisor.name
  account_name        = module.cosmos_db.name
  role_definition_id  = "${module.cosmos_db.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  principal_id        = module.function_app.principal_id
  scope               = module.cosmos_db.id
  depends_on          = [time_sleep.wait_for_func_identity, module.cosmos_db]
}

# ─── APIM Backends ─────────────────────────────────────────────────────────────
resource "azurerm_api_management_backend" "openai_backend" {
  provider            = azurerm.shared
  name                = "openai-backend-${var.workload}"
  resource_group_name = data.azurerm_resource_group.shared.name
  api_management_name = data.azurerm_api_management.shared.name
  protocol            = "http"
  url                 = "${module.openai.endpoint}openai"
  description         = "APIM backend for Azure OpenAI (TaxBot India)"
  depends_on          = [module.openai]
}

resource "azurerm_api_management_backend" "function_backend" {
  provider            = azurerm.shared
  name                = "func-backend-${var.workload}"
  resource_group_name = data.azurerm_resource_group.shared.name
  api_management_name = data.azurerm_api_management.shared.name
  protocol            = "http"
  url                 = "https://${module.function_app.default_hostname}/api"
  description         = "APIM backend for TaxBot India Function App"
  depends_on          = [module.function_app]
}

# ─── APIM API definition for TaxBot India ─────────────────────────────────────
# azapi_resource used — azurerm v4 triggers 400 ValidationError on Consumption APIM.
resource "azapi_resource" "apim_tax_advisor_api" {
  type      = "Microsoft.ApiManagement/service/apis@2022-08-01"
  name      = "taxb-tax-advisor"
  parent_id = data.azurerm_api_management.shared.id

  body = {
    properties = {
      displayName          = "TaxBot India — Tax Advisor"
      path                 = "tax-advisor"
      protocols            = ["https"]
      serviceUrl           = "https://${module.function_app.default_hostname}/api"
      subscriptionRequired = false
    }
  }

  depends_on = [azurerm_api_management_backend.function_backend]
}

# POST /chat
resource "azapi_resource" "chat_post" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "chat-post"
  parent_id = azapi_resource.apim_tax_advisor_api.id

  body = {
    properties = {
      displayName = "Chat"
      method      = "POST"
      urlTemplate = "/chat"
      description = "Conversational RAG tax advisor."
    }
  }

  depends_on = [azapi_resource.apim_tax_advisor_api]
}

# POST /compare-regime
resource "azapi_resource" "compare_regime_post" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "compare-regime-post"
  parent_id = azapi_resource.apim_tax_advisor_api.id

  body = {
    properties = {
      displayName = "Compare Tax Regime"
      method      = "POST"
      urlTemplate = "/compare-regime"
      description = "Structured old vs new regime tax comparison."
    }
  }

  depends_on = [azapi_resource.apim_tax_advisor_api]
}

# POST /analyse-salary
resource "azapi_resource" "analyse_salary_post" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "analyse-salary-post"
  parent_id = azapi_resource.apim_tax_advisor_api.id

  body = {
    properties = {
      displayName = "Analyse Salary Slip"
      method      = "POST"
      urlTemplate = "/analyse-salary"
      description = "Parse salary slip text and return tax breakdown."
    }
  }

  depends_on = [azapi_resource.apim_tax_advisor_api]
}

# POST /analyse-ctc
resource "azapi_resource" "analyse_ctc_post" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "analyse-ctc-post"
  parent_id = azapi_resource.apim_tax_advisor_api.id

  body = {
    properties = {
      displayName = "Analyse CTC"
      method      = "POST"
      urlTemplate = "/analyse-ctc"
      description = "CTC structure analysis and tax optimisation recommendations."
    }
  }

  depends_on = [azapi_resource.apim_tax_advisor_api]
}

# GET /health
resource "azapi_resource" "health_get" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "health-get"
  parent_id = azapi_resource.apim_tax_advisor_api.id

  body = {
    properties = {
      displayName = "Health Check"
      method      = "GET"
      urlTemplate = "/health"
      description = "Health check endpoint."
    }
  }

  depends_on = [azapi_resource.apim_tax_advisor_api]
}

# GET /diagnostics
resource "azapi_resource" "diagnostics_get" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "diagnostics-get"
  parent_id = azapi_resource.apim_tax_advisor_api.id

  body = {
    properties = {
      displayName = "Diagnostics"
      method      = "GET"
      urlTemplate = "/diagnostics"
      description = "Returns env var presence check."
    }
  }

  depends_on = [azapi_resource.apim_tax_advisor_api]
}

# ─── APIM Policy: CORS + forward to Function App ───────────────────────────────
resource "azapi_resource" "tax_advisor_cors_policy" {
  type      = "Microsoft.ApiManagement/service/apis/policies@2022-08-01"
  name      = "policy"
  parent_id = azapi_resource.apim_tax_advisor_api.id

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
        <header>Content-Type</header>
        <header>Authorization</header>
        <header>x-session-id</header>
      </allowed-headers>
      <expose-headers>
        <header>x-session-id</header>
      </expose-headers>
    </cors>
    <set-backend-service backend-id="func-backend-${var.workload}" />
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

  depends_on = [
    azapi_resource.apim_tax_advisor_api,
    azurerm_api_management_backend.function_backend,
  ]
}

# ─── Static Web App (Free tier) ────────────────────────────────────────────────
resource "azurerm_static_web_app" "frontend" {
  name                = module.taxb_stapp_name.name
  location            = var.swa_location
  resource_group_name = azurerm_resource_group.tax_advisor.name
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = local.tags
}
