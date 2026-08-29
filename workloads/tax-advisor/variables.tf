# ==============================================================================
# Workload: TaxBot India Variables
# Defines the schema and validation for TaxBot Serverless AI (Function App, SWA, Cosmos DB, AI Search).
# ==============================================================================

# ── Subscription & Core Region ───────────────────────────────────────────────

variable "subscription_id" {
  description = "Azure subscription ID for the TaxBot workload (Apps-prod)."
  type        = string
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

variable "swa_location" {
  description = "Azure region for Static Web App control plane."
  type        = string
  default     = "eastus2"
}

# ── CAF Resource Naming Tokens ──────────────────────────────────────────────

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

# ── Governance Tags ──────────────────────────────────────────────────────────

variable "company_name" {
  description = "Company name for tagging."
  type        = string
  default     = "HappyTechies"
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

# ── Network Architecture ────────────────────────────────────────────────────

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

# ── Hub Network Peering Lookups ──────────────────────────────────────────────

variable "hub_subscription_id" {
  description = "Azure subscription ID for the Hub environment."
  type        = string
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

# ── Shared Services Platform Lookups ─────────────────────────────────────────

variable "shared_subscription_id" {
  description = "Azure subscription ID for Shared Services."
  type        = string
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

variable "shared_key_vault_name" {
  description = "Name of the central Key Vault in Shared Services."
  type        = string
  default     = "kv-ht-ss-p-cin-01"
}

variable "shared_openai_name" {
  description = "Name of the shared Azure OpenAI account in platform/shared-services."
  type        = string
  default     = "oai-ht-ss-p-eus-01"
}

variable "shared_content_safety_name" {
  description = "Name of the shared Azure AI Content Safety account in platform/shared-services."
  type        = string
  default     = "cs-ht-ss-p-sea-01"
}

# ── Workload AI & RBAC Configurations ────────────────────────────────────────

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

variable "alert_email_address" {
  description = "Email address or distribution list for Azure Monitor operational alerts."
  type        = string
  default     = "ganesank@mytaxbot.site"
}

variable "enable_observability_agent" {
  description = "Whether to deploy the Azure Copilot Observability Agent for autonomous alert correlation."
  type        = bool
  default     = true
}

variable "observability_agent_location" {
  description = "Azure region for the Azure Copilot Observability Agent (must be a supported region e.g. eastus)."
  type        = string
  default     = "eastus"
}

variable "observability_agent_location_short" {
  description = "Short name of the Azure region for Observability Agent naming."
  type        = string
  default     = "eus"
}

# ── Custom Domain & Cloudflare DNS Configurations ───────────────────────────

variable "custom_domain_name" {
  description = "Custom domain for the TaxBot India frontend."
  type        = string
  default     = "www.mytaxbot.site"
}

variable "cloudflare_zone_id" {
  description = "The Cloudflare Zone ID for mytaxbot.site DNS management."
  type        = string
  default     = "45acc43e2f88066e0406eca94edffc53"
}

variable "app_prod_sp_object_id" {
  description = "Enterprise App Object ID (Principal ID) for the app-prod GitHub Actions & ADO deployment Service Principal."
  type        = string
}


