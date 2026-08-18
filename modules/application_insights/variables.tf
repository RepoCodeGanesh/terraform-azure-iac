variable "name" {
  description = "Name of the Application Insights component."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group where Application Insights will be created."
  type        = string
}

variable "location" {
  description = "Azure region for Application Insights."
  type        = string
}

variable "workspace_id" {
  description = "Resource ID of the Log Analytics Workspace to link."
  type        = string
}

variable "application_type" {
  description = "Type of application being monitored (web, other)."
  type        = string
  default     = "web"
}

variable "tags" {
  description = "Tags to assign to Application Insights."
  type        = map(string)
  default     = {}
}
