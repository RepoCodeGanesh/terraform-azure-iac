# ==============================================================================
# Workload: BankCompliance AI — API Management Routing Tier
# Purpose: APIM Backend, Regulatory API routes, Operations, and CORS Policy
# Cost:    $0.00 base cost (Consumption Tier APIM)
# ==============================================================================

module "bankc_apim_api" {
  source = "../../modules/apim_api"

  providers = {
    azurerm = azurerm.shared
  }

  apim_id                  = data.azurerm_api_management.shared.id
  apim_name                = data.azurerm_api_management.shared.name
  apim_resource_group_name = data.azurerm_resource_group.shared.name
  backend_name             = "aks-backend-${var.workload}"
  backend_url              = "http://bankc-api-ht-cin.centralindia.cloudapp.azure.com"
  backend_description      = "APIM backend for BankCompliance AKS backend"
  api_name                 = "bankc-compliance-api"
  display_name             = "BankCompliance AI — Regulatory Copilot"
  path                     = "bankc"

  operations = {
    "compliance-query-post" = {
      display_name = "Query Compliance"
      method       = "POST"
      url_template = "/api/v1/compliance/query"
      description  = "Submit regulatory compliance question"
    }
    "healthz-get" = {
      display_name = "Health Check"
      method       = "GET"
      url_template = "/healthz"
      description  = "Returns AKS backend health status"
    }
    "compliance-circulars-get" = {
      display_name = "List Master Directions"
      method       = "GET"
      url_template = "/api/v1/compliance/circulars"
      description  = "Returns list of indexed RBI circulars"
    }
  }
}

# ─── State Migration: Move legacy top-level APIM resources into module ─────────

moved {
  from = azurerm_api_management_backend.bankc_backend
  to   = module.bankc_apim_api.azurerm_api_management_backend.this
}

moved {
  from = azapi_resource.apim_bankc_api
  to   = module.bankc_apim_api.azapi_resource.api
}

moved {
  from = azapi_resource.bankc_cors_policy
  to   = module.bankc_apim_api.azapi_resource.policy
}

moved {
  from = azapi_resource.bankc_healthz_get
  to   = module.bankc_apim_api.azapi_resource.operations["healthz-get"]
}

moved {
  from = azapi_resource.compliance_circulars_get
  to   = module.bankc_apim_api.azapi_resource.operations["compliance-circulars-get"]
}

moved {
  from = azapi_resource.compliance_query_post
  to   = module.bankc_apim_api.azapi_resource.operations["compliance-query-post"]
}
