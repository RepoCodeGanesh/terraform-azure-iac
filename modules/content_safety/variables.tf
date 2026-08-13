variable "name" {
  type        = string
  description = "The name of the Azure AI Content Safety Cognitive Account."
}

variable "resource_group_name" {
  type        = string
  description = "Name of the resource group."
}

variable "location" {
  type        = string
  description = "Azure region location."
}

variable "sku_name" {
  type        = string
  description = "SKU for Content Safety. Defaults to F0 (Free tier)."
  default     = "F0"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
