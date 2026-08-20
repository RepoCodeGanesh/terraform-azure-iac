variable "name" {
  description = "Name of the Static Web App."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group where the Static Web App is created."
  type        = string
}

variable "location" {
  description = "Azure region for Static Web App control plane (e.g. eastus2, centralindia)."
  type        = string
  default     = "eastus2"
}

variable "sku_tier" {
  description = "SKU tier (Free or Standard)."
  type        = string
  default     = "Free"
}

variable "sku_size" {
  description = "SKU size (Free or Standard)."
  type        = string
  default     = "Free"
}

variable "app_settings" {
  description = "Map of app settings to configure on the Static Web App."
  type        = map(string)
  default     = {}
}

variable "custom_domain_name" {
  description = "Optional custom domain name (e.g. bank.mytaxbot.site)."
  type        = string
  default     = null
}

variable "custom_domain_validation_type" {
  description = "Validation type for custom domain (cname-delegation, dns-txt-token)."
  type        = string
  default     = "cname-delegation"
}

variable "tags" {
  description = "Tags to assign to the Static Web App."
  type        = map(string)
  default     = {}
}
