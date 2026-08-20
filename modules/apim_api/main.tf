# ==============================================================================
# Module: Azure API Management API & Operations (Composite)
# Purpose: Registers backend endpoints, publishes API routes, and applies CORS policies
# Cost:    $0.00 base cost (Consumption Tier — 1 million calls free / month)
# ==============================================================================

terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.0"
    }
  }
}

# ─── APIM Backend Definition ──────────────────────────────────────────────────
resource "azurerm_api_management_backend" "this" {
  name                = var.backend_name
  resource_group_name = var.apim_resource_group_name
  api_management_name = var.apim_name
  protocol            = var.backend_protocol
  url                 = var.backend_url
  description         = var.backend_description
}

# ─── APIM API Definition ──────────────────────────────────────────────────────
resource "azapi_resource" "api" {
  type      = "Microsoft.ApiManagement/service/apis@2022-08-01"
  name      = var.api_name
  parent_id = var.apim_id

  body = {
    properties = {
      displayName          = var.display_name
      path                 = var.path
      protocols            = var.protocols
      serviceUrl           = var.backend_url
      subscriptionRequired = var.subscription_required
    }
  }

  depends_on = [azurerm_api_management_backend.this]
}

# ─── APIM Operations ──────────────────────────────────────────────────────────
resource "azapi_resource" "operations" {
  for_each  = var.operations
  type      = "Microsoft.ApiManagement/service/apis/operations@2022-08-01"
  name      = each.key
  parent_id = azapi_resource.api.id

  body = {
    properties = {
      displayName = each.value.display_name
      method      = each.value.method
      urlTemplate = each.value.url_template
      description = try(each.value.description, each.value.display_name)
    }
  }

  depends_on = [azapi_resource.api]
}

# ─── APIM Policy (CORS + Forward Request) ─────────────────────────────────────
resource "azapi_resource" "policy" {
  type      = "Microsoft.ApiManagement/service/apis/policies@2022-08-01"
  name      = "policy"
  parent_id = azapi_resource.api.id

  body = {
    properties = {
      format = "xml"
      value = coalesce(var.custom_policy_xml, <<-XML
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
    <set-backend-service backend-id="${azurerm_api_management_backend.this.name}" />
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
      )
    }
  }

  depends_on = [
    azapi_resource.api,
    azurerm_api_management_backend.this
  ]
}
