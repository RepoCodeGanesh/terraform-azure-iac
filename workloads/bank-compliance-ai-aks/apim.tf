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
  backend_timeout          = 180

  operations = {
    # ─── Governed Catch-All Proxy (Universal Microservice Routing) ────────────
    # Automatically routes ANY new or dynamic FastAPI endpoint, FastMCP SSE route,
    # or parameterized sub-path (e.g. /graph/traverse/{item_id}) without requiring
    # manual ARM operation schema definitions or causing 404s.
    # Note: Detailed microservice endpoints (all 42 routes) are published dynamically
    # via `az apim api import` with /openapi.json in app-bank-compliance.yml.
    "all-routes-proxy" = {
      display_name = "Backend Microservice Route Proxy"
      method       = "*"
      url_template = "/*"
      description  = "Governed edge pass-through for all FastAPI & FastMCP microservice endpoints"
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
