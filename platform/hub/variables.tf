# ==============================================================================
# Platform: Hub Network Variables
# Defines the schema and validation for Hub VNet, Azure Firewall, Bastion, & Gateway.
# ==============================================================================

# ── Subscription & Core Region ───────────────────────────────────────────────

variable "subscription_id" {
  description = "Azure subscription ID for the hub environment (Hub-prod)."
  type        = string
}

variable "location" {
  description = "Azure region for hub resources."
  type        = string
  default     = "centralindia"
}

variable "location_short" {
  description = "Azure region short name."
  type        = string
  default     = "cin"
}

# ── CAF Resource Naming Tokens ──────────────────────────────────────────────

variable "project" {
  description = "Project code used in resource naming."
  type        = string
  default     = "ht"
}

variable "workload" {
  description = "Workload code used in resource naming."
  type        = string
  default     = "hub"
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

# ── Governance Tags ──────────────────────────────────────────────────────────

variable "company_name" {
  description = "Company name for tagging purposes."
  type        = string
  default     = "HappyTechies"
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

# ── Hub Network Architecture ────────────────────────────────────────────────

variable "vnet_address_space" {
  description = "CIDR block for the hub virtual network."
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "firewall_subnet_prefix" {
  description = "Firewall subnet prefix."
  type        = string
  default     = "10.0.0.0/26"
}

variable "bastion_subnet_prefix" {
  description = "Bastion subnet prefix."
  type        = string
  default     = "10.0.0.64/27"
}

variable "gateway_subnet_prefix" {
  description = "Gateway subnet prefix."
  type        = string
  default     = "10.0.0.96/27"
}

variable "management_subnet_prefix" {
  description = "Management subnet prefix."
  type        = string
  default     = "10.0.1.0/24"
}
