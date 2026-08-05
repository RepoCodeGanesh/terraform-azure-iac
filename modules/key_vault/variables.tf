variable "name" {
  description = "Name of the Key Vault."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group where the Key Vault will be created."
  type        = string
}

variable "location" {
  description = "Azure region for the Key Vault."
  type        = string
}

variable "tenant_id" {
  description = "The Azure AD tenant ID used for the Key Vault."
  type        = string
}

variable "sku_name" {
  description = "Sku name for the Key Vault."
  type        = string
  default     = "standard"
}

variable "enable_rbac_authorization" {
  description = "Whether RBAC authorization is enabled for the Key Vault."
  type        = bool
  default     = true
}

variable "public_network_access_enabled" {
  description = "Whether public network access is enabled for the Key Vault."
  type        = bool
  default     = true
}

variable "soft_delete_retention_days" {
  description = "The number of days to retain deleted vaults."
  type        = number
  default     = 7
}

variable "purge_protection_enabled" {
  description = "Whether purge protection is enabled."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to the Key Vault."
  type        = map(string)
  default     = {}
}