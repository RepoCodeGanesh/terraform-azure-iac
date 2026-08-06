variable "company" {
  description = "Company short name used in resource naming."
  type        = string
  default     = "ht"
}

variable "environment" {
  description = "Environment identifier for the resource."
  type        = string
}

variable "workload" {
  description = "Logical workload for the resource."
  type        = string
}

variable "location" {
  description = "Azure region for deployment."
  type        = string
  default     = "centralindia"
}

variable "region_code" {
  description = "Short region code used in naming."
  type        = string
  default     = "cin"
}

variable "instance" {
  description = "Instance index for naming."
  type        = string
  default     = "01"
}

variable "owner" {
  description = "Owner tag value."
  type        = string
}

variable "cost_center" {
  description = "Cost center tag value."
  type        = string
}

variable "project" {
  description = "Project tag value."
  type        = string
}

variable "tags" {
  description = "Additional tags to merge with standard ones."
  type        = map(string)
  default     = {}
}
