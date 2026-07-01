variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "centralindia"
}

variable "location_short" {
  description = "Short name for the Azure region"
  type        = string
  default     = "cind"
}

variable "hub_resource_group_name" {
  description = "Hub resource group name"
  type        = string
  default     = "ht-centralindia-dev-rg-hub-01"
}

variable "existing_key_vault_name" {
  description = "Existing key vault name"
  type        = string
  default     = "ht-cind-dev-kv-hub-02"
}

variable "existing_key_vault_secret_name" {
  description = "Existing key vault secret name"
  type        = string
  default     = "INFRACOST-API-KEY"
}

variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default = {
    environment = "dev"
    owner       = "platform"
    workload    = "hub-spoke-demo"
    managedBy   = "terraform"
  }
}
