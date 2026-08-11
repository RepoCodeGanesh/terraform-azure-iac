variable "name" {
  description = "Name of the Azure AI Search Service."
  type        = string
}

variable "location" {
  description = "Azure region for the Search Service."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name where the Search Service will be created."
  type        = string
}

variable "sku" {
  description = "SKU for the Search Service (default: free for $0/month)."
  type        = string
  default     = "free"
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}
