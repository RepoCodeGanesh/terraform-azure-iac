variable "name" {
  description = "Name of the Azure OpenAI Cognitive Account."
  type        = string
}

variable "location" {
  description = "Azure region for the Cognitive Account."
  type        = string
}

variable "resource_group_id" {
  description = "The full resource ID of the resource group where the OpenAI account will be created. Required by AVM module as parent_id."
  type        = string
}

variable "sku_name" {
  description = "SKU for the Cognitive Account (default: S0)."
  type        = string
  default     = "S0"
}

variable "custom_subdomain_name" {
  description = "Custom subdomain name for Cognitive Account."
  type        = string
  default     = null
}

variable "public_network_access_enabled" {
  description = "Enable public network access."
  type        = bool
  default     = true
}

variable "deployments" {
  description = "Map of model deployments to create inside the OpenAI account."
  type = map(object({
    model_format  = string
    model_name    = string
    model_version = string
    sku_name      = string
    sku_capacity  = number
  }))
  default = {}
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID for diagnostic settings."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}
