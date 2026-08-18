# ==============================================================================
# Workload: TaxBot India — API Management Gateway Tier
# Purpose: APIM Backends, published REST APIs (/chat, /compare-regime, etc.), and CORS Policy
# Cost:    $0.00 base cost (Consumption Tier APIM)
# ==============================================================================

# ─── APIM Backend for Direct OpenAI Integration ───────────────────────────────

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

# ─── APIM API & Operations for TaxBot India ───────────────────────────────────

module "taxb_apim_api" {
  source = "../../modules/apim_api"

  apim_id                  = data.azurerm_api_management.shared.id
  apim_name                = data.azurerm_api_management.shared.name
  apim_resource_group_name = data.azurerm_resource_group.shared.name
  backend_name             = "func-backend-${var.workload}"
  backend_url              = "https://${module.function_app.default_hostname}/api"
  backend_description      = "APIM backend for TaxBot India Function App"
  api_name                 = "taxb-tax-advisor"
  display_name             = "TaxBot India — Tax Advisor"
  path                     = "tax-advisor"

  operations = {
    "chat-post" = {
      display_name = "Chat"
      method       = "POST"
      url_template = "/chat"
      description  = "Conversational RAG tax advisor."
    }
    "compare-regime-post" = {
      display_name = "Compare Tax Regime"
      method       = "POST"
      url_template = "/compare-regime"
      description  = "Structured old vs new regime tax comparison."
    }
    "analyse-salary-post" = {
      display_name = "Analyse Salary Slip"
      method       = "POST"
      url_template = "/analyse-salary"
      description  = "Parse salary slip text and return tax breakdown."
    }
    "analyse-ctc-post" = {
      display_name = "Analyse CTC"
      method       = "POST"
      url_template = "/analyse-ctc"
      description  = "CTC structure analysis and tax optimisation recommendations."
    }
    "health-get" = {
      display_name = "Health Check"
      method       = "GET"
      url_template = "/health"
      description  = "Health check endpoint."
    }
    "diagnostics-get" = {
      display_name = "Diagnostics"
      method       = "GET"
      url_template = "/diagnostics"
      description  = "Returns env var presence check."
    }
  }

  custom_policy_xml = <<-XML
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
