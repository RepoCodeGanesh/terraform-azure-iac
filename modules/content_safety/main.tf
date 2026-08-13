# ==============================================================================
# Module: Azure AI Content Safety Service (Free F0 SKU)
# Purpose: AI Security, Jailbreak Shield & Content Safety Filtering
# ==============================================================================

resource "azurerm_cognitive_account" "content_safety" {
  name                  = var.name
  location              = var.location
  resource_group_name   = var.resource_group_name
  kind                  = "ContentSafety"
  sku_name              = var.sku_name
  custom_subdomain_name = var.name

  public_network_access_enabled = true

  tags = var.tags
}
