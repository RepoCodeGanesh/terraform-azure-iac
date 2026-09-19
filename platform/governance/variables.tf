variable "subscription_id" {
  type        = string
  description = "Default subscription ID for Terraform provider (Shared-services or Bootstrap)."
  default     = "859a785c-bd38-402d-b595-1f44f40fb9bf"
}

variable "root_management_group_id" {
  type        = string
  description = "Root Management Group ID"
  default     = "HappieTechies-root-MG"
}

variable "location" {
  type        = string
  description = "Primary deployment location for policy assignment identity"
  default     = "centralindia"
}
