# ==============================================================================
# Module: Azure Storage Account (Standard LRS / StorageV2)
# Purpose: General-purpose storage and tfstate backend container
# Cost:    Standard LRS ($0 base cost, pay per GB stored / operations)
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

resource "azurerm_storage_account" "this" {
  name                            = var.name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = var.account_tier
  account_replication_type        = var.account_replication_type
  account_kind                    = var.account_kind
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = var.public_network_access_enabled
  https_traffic_only_enabled      = true
  shared_access_key_enabled       = var.shared_access_key_enabled
  tags                            = var.tags

  blob_properties {
    delete_retention_policy {
      days = var.blob_retention_days
    }

    container_delete_retention_policy {
      days = var.container_retention_days
    }
  }
}

resource "azurerm_storage_container" "this" {
  count                 = var.container_name != null ? 1 : 0
  name                  = var.container_name
  storage_account_id    = azurerm_storage_account.this.id
  container_access_type = var.container_access_type
}
