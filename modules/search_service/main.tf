##############################################################
# Wrapper module for Azure AI Search (Search Service)
# Source: Azure/avm-res-search-searchservice/azurerm v0.3.0
# Azure Verified Module (AVM) - fully azurerm 4.x compatible
##############################################################

module "search_service" {
  source  = "Azure/avm-res-search-searchservice/azurerm"
  version = "0.3.0"

  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku
  tags                = var.tags
}
