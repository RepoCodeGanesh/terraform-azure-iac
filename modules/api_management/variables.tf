variable "name" {
  description = "API Management instance name."
  type        = string
}

variable "location" {
  description = "Azure region for API Management."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name where API Management is created."
  type        = string
}

variable "publisher_name" {
  description = "Publisher name for API Management."
  type        = string
}

variable "publisher_email" {
  description = "Publisher email for API Management."
  type        = string
}

variable "sku_name" {
  description = "API Management SKU."
  type        = string
  default     = "Consumption_0"
}

variable "virtual_network_type" {
  description = "Virtual network type for the API Management."
  type        = string
  default     = "None"
}

variable "public_ip_address_id" {
  description = "Public IP resource ID for the API Management gateway."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to the API Management instance."
  type        = map(string)
  default     = {}
}
