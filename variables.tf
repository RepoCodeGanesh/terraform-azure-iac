variable "tenant_id" {
  type        = string
  description = "Azure tenant ID"
  default     = "4cef0d84-84d6-4ed0-8abe-773b015bcf99"
}

variable "subscription_id" {
  type        = string
  description = "Azure subscription ID for the dev environment"
  default     = "859a785c-bd38-402d-b595-1f44f40fb9bf"
}

variable "environment" {
  type        = string
  description = "Single supported environment for this learning repo."
  default     = "dev"

  validation {
    condition     = var.environment == "dev"
    error_message = "This repository is intentionally dev-only. Use environment = \"dev\"."
  }
}

variable "location" {
  description = "Azure region for spoke resources."
  type        = string
  default     = "centralindia"
}

variable "resource_group_prefix" {
  description = "Naming prefix used for dev learning resources."
  type        = string
  default     = "ht-cind"
}

variable "workspace" {
  description = "Logical workspace suffix used in names and backend keys."
  type        = string
  default     = "root"
}

variable "hub_rg_name" {
  description = "Existing dev hub resource group."
  type        = string
  default     = "ht-cind-dev-rg-hub-01"
}

variable "hub_vnet_name" {
  description = "Existing dev hub virtual network name."
  type        = string
  default     = "ht-cind-dev-vnet-hub-01"
}

variable "hub_storage_account" {
  description = "Existing dev hub storage account for Terraform state."
  type        = string
  default     = "htcinddevsahub02"
}

variable "backend_container" {
  description = "Existing backend container in the dev hub storage account."
  type        = string
  default     = "tfstate"
}

variable "key_vault_name" {
  description = "Existing dev hub Key Vault used for references."
  type        = string
  default     = "ht-cind-dev-kv-hub-02"
}

variable "spoke_count" {
  description = "Number of learning spokes to create. Keep at 1 for the simple dev repo."
  type        = number
  default     = 1

  validation {
    condition     = var.spoke_count == 1
    error_message = "This simplified repo currently supports exactly one spoke."
  }
}

variable "spoke_address_space" {
  description = "CIDR range for the dev spoke VNet."
  type        = list(string)
  default     = ["10.42.0.0/16"]
}

variable "spoke_subnets" {
  description = "Subnet map for the dev spoke VNet."
  type = map(object({
    address_prefixes = list(string)
  }))
  default = {
    app = {
      address_prefixes = ["10.42.1.0/24"]
    }
    private_endpoints = {
      address_prefixes = ["10.42.2.0/24"]
    }
  }
}

variable "enabled_apps" {
  description = "App wrappers to instantiate. CI/CD validates operator selections against folders under apps/."
  type        = set(string)
  default     = ["staticwebapi", "serverless", "securems"]
}

variable "tags" {
  description = "Additional tags to merge with standard dev tags."
  type        = map(string)
  default     = {}
}
