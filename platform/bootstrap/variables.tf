variable "subscription_id" {
  description = "Azure subscription ID for the bootstrap subscription."
  type        = string
}

variable "location" {
  description = "Azure region for bootstrap resources."
  type        = string
  default     = "centralindia"
}

variable "location_short" {
  description = "Azure region short name."
  type        = string
  default     = "cin"
}

variable "company_name" {
  description = "Company name for tagging purposes."
  type        = string
  default     = "HappyTechies"
}

variable "project" {
  description = "Project code used in resource naming."
  type        = string
  default     = "ht"
}

variable "workload" {
  description = "Workload code used in resource naming."
  type        = string
  default     = "boot"
}

variable "environment" {
  description = "Environment code (d = dev, p = prod)."
  type        = string
  default     = "p"

  validation {
    condition     = contains(["d", "p"], var.environment)
    error_message = "Environment must be either 'd' or 'p'."
  }
}

variable "instance" {
  description = "Instance number."
  type        = string
  default     = "01"
}

variable "owner" {
  description = "Owner tag value."
  type        = string
  default     = "platform-team"
}

variable "cost_center" {
  description = "Cost center tag value."
  type        = string
  default     = "shared-services"
}

variable "tfstate_container_name" {
  description = "Name of the blob container that will hold Terraform state."
  type        = string
  default     = "tfstate"
}
