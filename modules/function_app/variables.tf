variable "name" {
  description = "Name of the Linux Function App."
  type        = string
}

variable "location" {
  description = "Azure region for resources."
  type        = string
}

variable "resource_group_id" {
  description = "Resource ID of the Resource Group where the Function App will be deployed. Used as parent_id for the AVM."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group. Used for inline Storage Account and Application Insights resources."
  type        = string
}

variable "storage_account_name" {
  description = "Name of the storage account for Function App backend."
  type        = string
}

variable "service_plan_id" {
  description = "Resource ID of the App Service Plan."
  type        = string
}

variable "python_version" {
  description = "Python version for Function App runtime stack."
  type        = string
  default     = "3.11"
}

variable "app_insights_name" {
  description = "Name of Application Insights resource."
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "ID of the Log Analytics Workspace for Application Insights."
  type        = string
}

variable "app_settings" {
  description = "Map of application settings for Function App."
  type        = map(string)
  default     = {}
}

variable "identity_type" {
  description = "Identity type (SystemAssigned, UserAssigned, SystemAssigned UserAssigned)."
  type        = string
  default     = "SystemAssigned"
}

variable "identity_ids" {
  description = "List of User-Assigned Identity resource IDs if identity_type includes UserAssigned."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}

variable "public_network_access_enabled" {
  description = "Controls whether public network access is enabled for the Function App."
  type        = bool
  default     = true
}

variable "minimum_tls_version" {
  description = "The minimum supported TLS version for the Function App. Defaults to 1.2 to support APIM Consumption gateway."
  type        = string
  default     = "1.2"
}
