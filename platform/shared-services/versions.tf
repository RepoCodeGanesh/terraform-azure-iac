terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-ht-boot-p-cin-01"
    storage_account_name = "sthtbootpcin01"
    container_name       = "tfstate"
    key                  = "shared-services/prod.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

provider "azurerm" {
  alias = "hub"
  features {}
  subscription_id = var.hub_subscription_id
}
