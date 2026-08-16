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

# taxb_oai_name removed — Azure OpenAI is now shared via platform/shared-services

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

# taxb_cs_name removed — Content Safety is now shared via platform/shared-services

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


# ─── Shared Azure OpenAI (from platform/shared-services) ──────────────────────
data "azurerm_cognitive_account" "openai" {
  provider            = azurerm.shared
  name                = var.shared_openai_name
  resource_group_name = var.shared_resource_group_name
}

# ─── Shared Azure AI Content Safety (from platform/shared-services) ───────────
data "azurerm_cognitive_account" "content_safety" {
  provider            = azurerm.shared
  name                = var.shared_content_safety_name
  resource_group_name = var.shared_resource_group_name
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

# ─── Azure AI Search (Free tier — tax document RAG index) ─────────────────────
module "search_service" {
  source = "../../modules/search_service"

  name                = module.taxb_srch_name.name
  location            = azurerm_resource_group.tax_advisor.location
  resource_group_name = azurerm_resource_group.tax_advisor.name
  sku                 = "free"

  tags = local.tags
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

# ─── Data source for Function App Identity (Prevents role assignment replacement drift) ──
data "azurerm_linux_function_app" "taxb_func" {
  name                = module.taxb_func_name.name
  resource_group_name = azurerm_resource_group.tax_advisor.name
  depends_on          = [module.function_app]
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
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity]
}

resource "azurerm_role_assignment" "func_openai_user" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = data.azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, data.azurerm_cognitive_account.openai]
}

resource "azurerm_role_assignment" "func_search_reader" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.search_service.id
  role_definition_name = "Search Index Data Reader"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, module.search_service]
}

resource "azurerm_cosmosdb_sql_role_assignment" "func_cosmos_contributor" {
  count               = var.enable_role_assignments ? 1 : 0
  resource_group_name = azurerm_resource_group.tax_advisor.name
  account_name        = module.cosmos_db.name
  role_definition_id  = "${module.cosmos_db.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  principal_id        = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  scope               = module.cosmos_db.id
  depends_on          = [time_sleep.wait_for_func_identity, module.cosmos_db]
}

resource "azurerm_role_assignment" "func_content_safety_user" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = data.azurerm_cognitive_account.content_safety.id
  role_definition_name = "Cognitive Services User"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, data.azurerm_cognitive_account.content_safety]
}

# ─── APIM Backends ─────────────────────────────────────────────────────────────
resource "azurerm_api_management_backend" "openai_backend" {
  provider            = azurerm.shared
  name                = "openai-backend-${var.workload}"
  resource_group_name = data.azurerm_resource_group.shared.name
  api_management_name = data.azurerm_api_management.shared.name
  protocol            = "http"
  url                 = "${data.azurerm_cognitive_account.openai.endpoint}openai"
  description         = "APIM backend for Azure OpenAI (TaxBot India)"
  depends_on          = [data.azurerm_cognitive_account.openai]
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

  app_settings = {
    "APPINSIGHTS_INSTRUMENTATIONKEY"        = module.function_app.app_insights_instrumentation_key
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = module.function_app.app_insights_connection_string
  }

  lifecycle {
    ignore_changes = [
      repository_url,
      repository_branch
    ]
  }

  tags = local.tags
}

# ─── SWA Deployment Token stored in Central Key Vault ─────────────────────────
resource "azurerm_key_vault_secret" "taxb_swa_api_token" {
  provider     = azurerm.shared
  name         = "taxb-swa-deployment-token"
  value        = azurerm_static_web_app.frontend.api_key
  key_vault_id = data.azurerm_key_vault.shared.id
  tags         = local.tags

  depends_on = [
    azurerm_static_web_app.frontend,
    data.azurerm_key_vault.shared
  ]
}

# ─── MONITORING & OBSERVABILITY: Diagnostic Settings ──────────────────────────

resource "azurerm_monitor_diagnostic_setting" "search_diagnostics" {
  name                       = "ds-srch-taxb-p-cin-01"
  target_resource_id         = module.search_service.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  enabled_log {
    category = "OperationLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

resource "azurerm_monitor_diagnostic_setting" "cosmos_diagnostics" {
  name                       = "ds-cosmos-taxb-p-cin-01"
  target_resource_id         = module.cosmos_db.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  enabled_log {
    category = "DataPlaneRequests"
  }

  enabled_log {
    category = "QueryRuntimeStatistics"
  }

  enabled_log {
    category = "PartitionKeyRUConsumption"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

# ─── MONITORING & OBSERVABILITY: Metric Alerts ────────────────────────────────

resource "azurerm_monitor_action_group" "taxb_ops" {
  name                = "ag-taxb-ops-p-cin-01"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  short_name          = "TaxbOps"

  tags = local.tags
}

resource "azurerm_monitor_metric_alert" "function_high_errors" {
  name                = "alert-func-high-5xx-errors"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  scopes              = [module.function_app.id]
  description         = "Triggers when Function App experiences > 5 server errors (HTTP 5xx) in 5 minutes."
  severity            = 1
  frequency           = "PT1M"
  window_size         = "PT5M"
  enabled             = false # Disabled to maintain $0.00 idle cost; enable as needed in production

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "Http5xx"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5
  }

  action {
    action_group_id = azurerm_monitor_action_group.taxb_ops.id
  }

  tags = local.tags
}

resource "azurerm_monitor_metric_alert" "openai_throttling" {
  name                = "alert-openai-throttled-429"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  scopes              = [data.azurerm_cognitive_account.openai.id]
  description         = "Triggers when Azure OpenAI rate limit (HTTP 429) throttling is encountered."
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"
  enabled             = true # Active primary quota & rate limit guardian (~$0.10/month)

  criteria {
    metric_namespace = "Microsoft.CognitiveServices/accounts"
    metric_name      = "BlockedCalls"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 1
  }

  action {
    action_group_id = azurerm_monitor_action_group.taxb_ops.id
  }

  tags = local.tags
}

# ─── Content Safety Diagnostics & Security Alerts ─────────────────────────────
resource "azurerm_monitor_diagnostic_setting" "cs_diagnostics" {
  name                       = "ds-cs-taxb-p-cin-01"
  target_resource_id         = data.azurerm_cognitive_account.content_safety.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  enabled_log {
    category = "Audit"
  }

  enabled_log {
    category = "RequestResponse"
  }

  enabled_metric {
    category = "AllMetrics"
  }

  depends_on = [
    data.azurerm_cognitive_account.content_safety,
    data.azurerm_log_analytics_workspace.shared
  ]
}

resource "azurerm_monitor_metric_alert" "cs_jailbreak_alert" {
  name                = "alert-cs-jailbreak-detected"
  resource_group_name = azurerm_resource_group.tax_advisor.name
  scopes              = [data.azurerm_cognitive_account.content_safety.id]
  description         = "Triggers when Azure AI Content Safety blocks >5 prompt injection/jailbreak attempts in 15 mins."
  severity            = 1
  frequency           = "PT5M"
  window_size         = "PT15M"
  enabled             = false # Disabled to maintain $0.00 idle cost; enable as needed in production

  criteria {
    metric_namespace = "Microsoft.CognitiveServices/accounts"
    metric_name      = "BlockedCalls"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5
  }

  action {
    action_group_id = azurerm_monitor_action_group.taxb_ops.id
  }

  tags = local.tags

  depends_on = [
    data.azurerm_cognitive_account.content_safety,
    azurerm_monitor_action_group.taxb_ops
  ]
}



