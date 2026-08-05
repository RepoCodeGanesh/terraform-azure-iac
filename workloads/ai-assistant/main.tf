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

# Naming modules
module "aiast_rg_name" {
  source = "../../modules/naming"

  resource_type  = "rg"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_vnet_name" {
  source = "../../modules/naming"

  resource_type  = "vnet"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_oai_name" {
  source = "../../modules/naming"

  resource_type  = "oai"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.openai_location_short
  instance       = var.instance
}

module "aiast_asp_name" {
  source = "../../modules/naming"

  resource_type  = "asp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_st_name" {
  source = "../../modules/naming"

  resource_type  = "st"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_func_name" {
  source = "../../modules/naming"

  resource_type  = "func"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_appi_name" {
  source = "../../modules/naming"

  resource_type  = "appi"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_cosmos_name" {
  source = "../../modules/naming"

  resource_type  = "cosmos"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_srch_name" {
  source = "../../modules/naming"

  resource_type  = "srch"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

module "aiast_stapp_name" {
  source = "../../modules/naming"

  resource_type  = "stapp"
  project        = var.project
  workload       = var.workload
  environment    = var.environment
  location_short = var.location_short
  instance       = var.instance
}

# Resource Group for DevOnboard AI workload
resource "azurerm_resource_group" "ai_assistant" {
  name     = module.aiast_rg_name.name
  location = var.location
  tags     = local.tags
}

# Spoke Virtual Network using network wrapper module
module "aiast_vnet" {
  source = "../../modules/network"

  resource_group_name = azurerm_resource_group.ai_assistant.name
  location            = azurerm_resource_group.ai_assistant.location
  vnet_name           = module.aiast_vnet_name.name
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

# Bi-directional VNet Peering to Hub
module "aiast_to_hub_peering" {
  source = "../../modules/vnet_peering"

  providers = {
    azurerm.vnet_1 = azurerm
    azurerm.vnet_2 = azurerm.hub
  }

  vnet_1_name = module.aiast_vnet.vnet_name
  vnet_1_rg   = azurerm_resource_group.ai_assistant.name
  vnet_1_id   = module.aiast_vnet.vnet_id

  vnet_2_name = data.azurerm_virtual_network.hub.name
  vnet_2_rg   = data.azurerm_resource_group.hub.name
  vnet_2_id   = data.azurerm_virtual_network.hub.id

  depends_on = [
    module.aiast_vnet
  ]
}

# Azure OpenAI via Cognitive Account Wrapper Module
module "openai" {
  source = "../../modules/cognitive_account"

  name                       = module.aiast_oai_name.name
  location                   = var.openai_location
  resource_group_id          = azurerm_resource_group.ai_assistant.id
  sku_name                   = "S0"
  custom_subdomain_name      = module.aiast_oai_name.name
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id

  deployments = {
    (var.openai_model_name) = {
      model_format  = "OpenAI"
      model_name    = var.openai_model_name
      model_version = var.openai_model_version
      sku_name      = "GlobalStandard"
      sku_capacity  = 10 # 10k tokens/min cap – keeps cost near $0 idle
    }
  }

  tags = local.tags
}

# Cosmos DB (NoSQL) Free Tier for AI chat memory and session history
module "cosmos_db" {
  source = "../../modules/cosmos_db"

  name                = module.aiast_cosmos_name.name
  location            = azurerm_resource_group.ai_assistant.location
  resource_group_name = azurerm_resource_group.ai_assistant.name
  enable_free_tier    = true

  tags = local.tags
}

# Azure AI Search (Free Tier for RAG vector search & indexing)
module "search_service" {
  source = "../../modules/search_service"

  name                = module.aiast_srch_name.name
  location            = azurerm_resource_group.ai_assistant.location
  resource_group_name = azurerm_resource_group.ai_assistant.name
  sku                 = "free"

  tags = local.tags
}

# App Service Plan for the workload Function App (Y1 Consumption — $0 idle)
module "aiast_service_plan" {
  source = "../../modules/service_plan"

  name                = module.aiast_asp_name.name
  location            = azurerm_resource_group.ai_assistant.location
  resource_group_name = azurerm_resource_group.ai_assistant.name
  os_type             = "Linux"
  sku_name            = "Y1"
  tags                = local.tags
}

# Serverless Function App via Function App Wrapper Module
module "function_app" {
  source = "../../modules/function_app"

  name                       = module.aiast_func_name.name
  location                   = azurerm_resource_group.ai_assistant.location
  resource_group_id          = azurerm_resource_group.ai_assistant.id
  resource_group_name        = azurerm_resource_group.ai_assistant.name
  storage_account_name       = module.aiast_st_name.name
  service_plan_id            = module.aiast_service_plan.id
  app_insights_name          = module.aiast_appi_name.name
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.shared.id
  python_version             = "3.11"
  identity_type              = "SystemAssigned"

  app_settings = {
    "AZURE_OPENAI_ENDPOINT"   = module.openai.endpoint
    "AZURE_OPENAI_MODEL"      = "gpt-5.4-nano"
    "COSMOS_DB_ENDPOINT"      = module.cosmos_db.endpoint
    "COSMOS_DB_DATABASE"      = module.cosmos_db.database_name
    "COSMOS_DB_CONTAINER"     = module.cosmos_db.container_name
    "AZURE_SEARCH_ENDPOINT"   = module.search_service.endpoint
    "AZURE_SEARCH_INDEX"      = "devonboard-docs"
    "RAG_DOCUMENTS_CONTAINER" = "documents"
    "APP_NAME"                = "DevOnboard AI"
    "APP_VERSION"             = "1.0.0"
  }

  tags = local.tags
}

# Storage Container for RAG Documents (PDFs, Word docs, text files)
resource "azurerm_storage_container" "rag_documents" {
  name                  = "documents"
  storage_account_id    = module.function_app.storage_account_id
  container_access_type = "private"

  depends_on = [
    module.function_app
  ]
}

# Wait 10s for System-Assigned Managed Identity propagation in Entra ID (prevents PrincipalNotFound errors)
resource "time_sleep" "wait_for_func_identity" {
  create_duration = "10s"

  depends_on = [
    module.function_app
  ]
}

# Role Assignment: Grant "Storage Blob Data Contributor" to Function App System-Assigned Identity
resource "azurerm_role_assignment" "func_blob_contributor" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.function_app.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.function_app.principal_id

  depends_on = [
    time_sleep.wait_for_func_identity
  ]
}

# Role Assignment: Grant "Cognitive Services OpenAI User" to Function App System-Assigned Identity
resource "azurerm_role_assignment" "func_openai_user" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.function_app.principal_id

  depends_on = [
    time_sleep.wait_for_func_identity,
    module.openai
  ]
}

# Role Assignment: Grant "Search Index Data Reader" to Function App System-Assigned Identity
resource "azurerm_role_assignment" "func_search_reader" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = module.search_service.id
  role_definition_name = "Search Index Data Reader"
  principal_id         = module.function_app.principal_id

  depends_on = [
    time_sleep.wait_for_func_identity,
    module.search_service
  ]
}

# Role Assignment: Grant Cosmos DB Data Contributor to Function App System-Assigned Identity
resource "azurerm_cosmosdb_sql_role_assignment" "func_cosmos_contributor" {
  count               = var.enable_role_assignments ? 1 : 0
  resource_group_name = azurerm_resource_group.ai_assistant.name
  account_name        = module.cosmos_db.name
  role_definition_id  = "${module.cosmos_db.id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  principal_id        = module.function_app.principal_id
  scope               = module.cosmos_db.id

  depends_on = [
    time_sleep.wait_for_func_identity,
    module.cosmos_db
  ]
}

# Register OpenAI Backend in Shared APIM (for direct OpenAI passthrough if needed)
resource "azurerm_api_management_backend" "openai_backend" {
  provider            = azurerm.shared
  name                = "openai-backend-${var.workload}"
  resource_group_name = data.azurerm_resource_group.shared.name
  api_management_name = data.azurerm_api_management.shared.name
  protocol            = "http"
  url                 = "${module.openai.endpoint}openai"

  description = "APIM backend for Azure OpenAI (gpt-4o-mini)"

  depends_on = [
    module.openai
  ]
}

# Register Function App as an APIM backend (chat handler)
resource "azurerm_api_management_backend" "function_backend" {
  provider            = azurerm.shared
  name                = "func-backend-${var.workload}"
  resource_group_name = data.azurerm_resource_group.shared.name
  api_management_name = data.azurerm_api_management.shared.name
  protocol            = "http"
  url                 = "https://${module.function_app.default_hostname}/api"

  description = "APIM backend for DevOnboard AI Function App chat handler"

  depends_on = [
    module.function_app
  ]
}

# ─── Import pre-existing APIM API into Terraform state ────────────────────────
# The API "dvob-ai-assistant" and its child resources were created by a prior
# apply but are not in state. These import blocks (Terraform ≥ 1.5) adopt them
# automatically during plan/apply. All blocks are idempotent — silently skipped
# once resources are in state. Safe to remove after first successful apply.
import {
  to = azapi_resource.apim_ai_assistant_api
  id = "/subscriptions/859a785c-bd38-402d-b595-1f44f40fb9bf/resourceGroups/rg-ht-ss-p-cin-01/providers/Microsoft.ApiManagement/service/apim-ht-ss-p-cin-01/apis/dvob-ai-assistant"
}

import {
  to = azapi_resource.chat_post
  id = "/subscriptions/859a785c-bd38-402d-b595-1f44f40fb9bf/resourceGroups/rg-ht-ss-p-cin-01/providers/Microsoft.ApiManagement/service/apim-ht-ss-p-cin-01/apis/dvob-ai-assistant/operations/chat-post"
}

import {
  to = azapi_resource.health_get
  id = "/subscriptions/859a785c-bd38-402d-b595-1f44f40fb9bf/resourceGroups/rg-ht-ss-p-cin-01/providers/Microsoft.ApiManagement/service/apim-ht-ss-p-cin-01/apis/dvob-ai-assistant/operations/health-get"
}

import {
  to = azapi_resource.diagnostics_get
  id = "/subscriptions/859a785c-bd38-402d-b595-1f44f40fb9bf/resourceGroups/rg-ht-ss-p-cin-01/providers/Microsoft.ApiManagement/service/apim-ht-ss-p-cin-01/apis/dvob-ai-assistant/operations/diagnostics-get"
}

import {
  to = azapi_resource.ai_assistant_cors_policy
  id = "/subscriptions/859a785c-bd38-402d-b595-1f44f40fb9bf/resourceGroups/rg-ht-ss-p-cin-01/providers/Microsoft.ApiManagement/service/apim-ht-ss-p-cin-01/apis/dvob-ai-assistant/policies/policy"
}

# ─── APIM API definition for DevOnboard AI Assistant ──────────────────────────
# azapi_resource used — azurerm v4 triggers 400 ValidationError on Consumption APIM.
# One name everywhere: ARM resource name = gateway path = "dvob-ai-assistant"
resource "azapi_resource" "apim_ai_assistant_api" {
  type      = "Microsoft.ApiManagement/service/apis@2022-08-01"
  name      = "dvob-ai-assistant"
  parent_id = data.azurerm_api_management.shared.id

  body = {
    properties = {
      displayName          = "DevOnboard AI Assistant"
      path                 = "dvob-ai-assistant"
      protocols            = ["https"]
      serviceUrl           = "https://${module.function_app.default_hostname}/api"
      subscriptionRequired = false
    }
  }

  depends_on = [
    azurerm_api_management_backend.function_backend
  ]
}


# POST /chat operation
resource "azapi_resource" "chat_post" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "chat-post"
  parent_id = azapi_resource.apim_ai_assistant_api.id

  body = {
    properties = {
      displayName = "Chat"
      method      = "POST"
      urlTemplate = "/chat"
      description = "Send a chat message to the DevOnboard AI assistant."
    }
  }

  depends_on = [azapi_resource.apim_ai_assistant_api]
}

# GET /health operation
resource "azapi_resource" "health_get" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "health-get"
  parent_id = azapi_resource.apim_ai_assistant_api.id

  body = {
    properties = {
      displayName = "Health Check"
      method      = "GET"
      urlTemplate = "/health"
      description = "Health check endpoint for the DevOnboard AI backend."
    }
  }

  depends_on = [azapi_resource.apim_ai_assistant_api]
}

# GET /diagnostics operation
resource "azapi_resource" "diagnostics_get" {
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = "diagnostics-get"
  parent_id = azapi_resource.apim_ai_assistant_api.id

  body = {
    properties = {
      displayName = "Diagnostics"
      method      = "GET"
      urlTemplate = "/diagnostics"
      description = "Returns which required env vars are configured (no values exposed)."
    }
  }

  depends_on = [azapi_resource.apim_ai_assistant_api]
}


# APIM Policy: CORS + forward to Function App backend
# azapi_resource used because the parent API is also managed by azapi.
resource "azapi_resource" "ai_assistant_cors_policy" {
  type      = "Microsoft.ApiManagement/service/apis/policies@2022-08-01"
  name      = "policy"
  parent_id = azapi_resource.apim_ai_assistant_api.id

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
    azapi_resource.apim_ai_assistant_api,
    azurerm_api_management_backend.function_backend,
  ]
}

# Static Web App for AI Assistant React Frontend (Free tier)
resource "azurerm_static_web_app" "frontend" {
  name                = module.aiast_stapp_name.name
  location            = var.swa_location
  resource_group_name = azurerm_resource_group.ai_assistant.name
  sku_tier            = "Free"
  sku_size            = "Free"

  tags = local.tags
}


