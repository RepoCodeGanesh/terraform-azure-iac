terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

resource "azurerm_key_vault" "this" {
  name                          = var.name
  resource_group_name           = var.resource_group_name
  location                      = var.location
  tenant_id                     = var.tenant_id
  sku_name                      = var.sku_name
  rbac_authorization_enabled    = var.enable_rbac_authorization
  public_network_access_enabled = var.public_network_access_enabled
  soft_delete_retention_days    = var.soft_delete_retention_days
  purge_protection_enabled      = var.purge_protection_enabled
  tags                          = var.tags

  network_acls {
    bypass         = "None"
    default_action = "Allow"
  }
}

