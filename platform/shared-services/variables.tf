variable "subscription_id" {
  description = "Azure subscription ID for the shared services environment."
  type        = string
  default     = "859a785c-bd38-402d-b595-1f44f40fb9bf"
}

variable "location" {
  description = "Azure region for shared services resources."
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
  default     = "ss"
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

variable "vnet_address_space" {
  description = "CIDR block for the shared services virtual network."
  type        = list(string)
  default     = ["10.30.0.0/16"]
}

variable "management_subnet_prefix" {
  description = "Management subnet prefix for admin and shared utilities."
  type        = string
  default     = "10.30.0.0/24"
}

variable "shared_services_subnet_prefix" {
  description = "Subnet prefix for shared platform services."
  type        = string
  default     = "10.30.1.0/24"
}

variable "private_endpoints_subnet_prefix" {
  description = "Subnet prefix for private endpoints."
  type        = string
  default     = "10.30.2.0/24"
}

variable "publisher_name" {
  description = "Publisher name used by API Management."
  type        = string
  default     = "HappyTechies"
}

variable "publisher_email" {
  description = "Publisher email used by API Management."
  type        = string
  default     = "platform-team@contoso.com"
}

variable "log_analytics_retention_days" {
  description = "Retention period for the Log Analytics workspace in days."
  type        = number
  default     = 30
}

variable "private_dns_zone_name" {
  description = "Private DNS zone name for Key Vault private endpoint."
  type        = string
  default     = "privatelink.vaultcore.azure.net"
}

variable "hub_subscription_id" {
  description = "Azure subscription ID for the Hub environment."
  type        = string
  default     = "3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b"
}

variable "hub_resource_group_name" {
  description = "Name of the Hub resource group for peering lookup."
  type        = string
  default     = "rg-ht-hub-p-cin-01"
}

variable "hub_vnet_name" {
  description = "Name of the Hub virtual network for peering lookup."
  type        = string
  default     = "vnet-ht-hub-p-cin-01"
}

variable "content_safety_location" {
  description = "Azure region for the shared Content Safety account (must be a supported region)."
  type        = string
  default     = "southeastasia"
}

variable "content_safety_location_short" {
  description = "Short name of the Azure region for shared Content Safety naming."
  type        = string
  default     = "sea"
}

variable "openai_location" {
  description = "Azure region for the shared Azure OpenAI account (e.g. eastus)."
  type        = string
  default     = "eastus"
}

variable "openai_location_short" {
  description = "Short name of the Azure region for shared OpenAI naming."
  type        = string
  default     = "eus"
}

variable "openai_model_name" {
  description = "Model name to deploy on the shared Azure OpenAI account."
  type        = string
  default     = "gpt-5.4-nano"
}

variable "openai_model_version" {
  description = "API version of the OpenAI model deployment."
  type        = string
  default     = "2026-03-17"
}

variable "openai_model_capacity" {
  description = "TPM capacity (in thousands) for the OpenAI model deployment."
  type        = number
  default     = 10
}
