# ==============================================================================
# Module: Azure Static Web App (Free Tier)
# Purpose: Serverless frontend hosting for React / Vite single-page applications
# Cost:    $0.00 / Month (Free Tier — 100 GB bandwidth, free SSL, custom domains)
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

resource "azurerm_static_web_app" "this" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_tier            = var.sku_tier
  sku_size            = var.sku_size
  app_settings        = var.app_settings

  lifecycle {
    ignore_changes = [
      repository_url,
      repository_branch
    ]
  }

  tags = var.tags
}

resource "azurerm_static_web_app_custom_domain" "this" {
  count             = var.custom_domain_name != null ? 1 : 0
  static_web_app_id = azurerm_static_web_app.this.id
  domain_name       = var.custom_domain_name
  validation_type   = var.custom_domain_validation_type

  depends_on = [azurerm_static_web_app.this]
}
