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
    # ─── Governed Catch-All Proxy (Universal Microservice Routing) ────────────
    # Automatically routes ANY new or dynamic FastAPI endpoint, FastMCP SSE route,
    # or parameterized sub-path (e.g. /graph/traverse/{item_id}) without requiring
    # manual ARM operation schema definitions or causing 404s.
    "all-routes-proxy" = {
      display_name = "Backend Microservice Route Proxy"
      method       = "*"
      url_template = "/*"
      description  = "Governed edge pass-through for all FastAPI & FastMCP microservice endpoints"
    }

    "compliance-query-post" = {
      display_name = "Query Compliance"
      method       = "POST"
      url_template = "/api/v1/compliance/query"
      description  = "Submit regulatory compliance question"
    }
    "compliance-query-v2-post" = {
      display_name = "Query Compliance v2 (LangGraph)"
      method       = "POST"
      url_template = "/api/v2/compliance/query"
      description  = "Submit regulatory compliance question using LangGraph cyclic StateGraph"
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
    "compliance-mcp-tools-get" = {
      display_name = "List MCP Tools"
      method       = "GET"
      url_template = "/api/v1/compliance/mcp/tools"
      description  = "Returns local bridge manifest and live FastMCP server tool catalog"
    }
    "compliance-mcp-call-post" = {
      display_name = "Call MCP Tool"
      method       = "POST"
      url_template = "/api/v1/compliance/mcp/call"
      description  = "Executes a regulatory FastMCP tool or deterministic compliance bridge tool"
    }
    "compliance-dossier-get" = {
      display_name = "Regulatory Compliance Dossier"
      method       = "GET"
      url_template = "/api/v1/compliance/dossier"
      description  = "Compiles auditor-ready compliance attestation dossier"
    }
    "compliance-stats-get" = {
      display_name = "Regulatory Compliance Stats"
      method       = "GET"
      url_template = "/api/v1/compliance/stats"
      description  = "Returns regulatory lake indexing and corpus statistics"
    }
    "compliance-ingest-post" = {
      display_name = "Trigger Corpus Ingestion"
      method       = "POST"
      url_template = "/api/v1/compliance/ingest"
      description  = "Triggers live ingestion of RBI circulars into vector store"
    }
    "compliance-redline-post" = {
      display_name = "Redline Contract Clause"
      method       = "POST"
      url_template = "/api/v1/compliance/redline"
      description  = "Audits contract clause text against regulatory rules"
    }
    "compliance-attestation-generate-post" = {
      display_name = "Generate Attestation Certificate"
      method       = "POST"
      url_template = "/api/v1/compliance/attestation/generate"
      description  = "Generates signed Board / RBI Audit Readiness Attestation Certificate"
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
