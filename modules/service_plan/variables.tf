variable "name" {
  description = "Name of the App Service Plan."
  type        = string
}

variable "location" {
  description = "Azure region for the App Service Plan."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group where the App Service Plan is created."
  type        = string
}

variable "os_type" {
  description = "Operating system type for the plan."
  type        = string
  default     = "Linux"
}

variable "sku_name" {
  description = "SKU name for the App Service Plan."
  type        = string
  default     = "F1"
}

variable "tags" {
  description = "Tags to apply to the App Service Plan."
  type        = map(string)
  default     = {}
}
