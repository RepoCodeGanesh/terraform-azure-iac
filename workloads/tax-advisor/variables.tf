variable "subscription_id" {
  description = "Azure subscription ID for the TaxBot workload (Apps-prod)."
  type        = string
  default     = "f4ffefe1-d689-4059-969c-ccc73e2a11d4"
}

variable "location" {
  description = "Azure region for workload resources."
  type        = string
  default     = "centralindia"
}

variable "location_short" {
  description = "Azure region short name."
  type        = string
  default     = "cin"
}

variable "openai_location" {
  description = "Azure region for Azure OpenAI account."
  type        = string
  default     = "eastus"
}

variable "openai_location_short" {
  description = "Azure region short name for Azure OpenAI resources."
  type        = string
  default     = "eus"
}

variable "swa_location" {
  description = "Azure region for Static Web App control plane."
  type        = string
  default     = "eastus2"
}

variable "company_name" {
  description = "Company name for tagging."
  type        = string
  default     = "HappyTechies"
}

variable "project" {
  description = "Project code used in resource naming."
  type        = string
  default     = "ht"
}

variable "workload" {
  description = "Workload code used in resource naming. TaxBot uses 'taxb'."
  type        = string
  default     = "taxb"
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
  default     = "ai-platform-team"
}

variable "cost_center" {
  description = "Cost center tag value."
  type        = string
  default     = "taxbot-india"
}

variable "vnet_address_space" {
  description = "CIDR block for the TaxBot spoke virtual network."
  type        = list(string)
  default     = ["10.41.0.0/16"]
}

variable "app_subnet_prefix" {
  description = "Subnet prefix for Function App regional VNet integration."
  type        = string
  default     = "10.41.1.0/24"
}

variable "private_endpoints_subnet_prefix" {
  description = "Subnet prefix for Private Endpoints."
  type        = string
  default     = "10.41.2.0/24"
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

variable "shared_subscription_id" {
  description = "Azure subscription ID for Shared Services."
  type        = string
  default     = "859a785c-bd38-402d-b595-1f44f40fb9bf"
}

variable "shared_resource_group_name" {
  description = "Name of Shared Services resource group."
  type        = string
  default     = "rg-ht-ss-p-cin-01"
}

variable "shared_law_name" {
  description = "Name of the shared Log Analytics Workspace."
  type        = string
  default     = "law-ht-ss-p-cin-01"
}

variable "shared_apim_name" {
  description = "Name of the shared API Management instance."
  type        = string
  default     = "apim-ht-ss-p-cin-01"
}

variable "openai_model_name" {
  description = "Name of the OpenAI model to deploy."
  type        = string
  default     = "gpt-5.4-nano"
}

variable "openai_model_version" {
  description = "Version of the OpenAI model to deploy."
  type        = string
  default     = "2026-03-17"
}

variable "enable_role_assignments" {
  description = "Whether to create RBAC role assignments for Function App identity."
  type        = bool
  default     = true
}
