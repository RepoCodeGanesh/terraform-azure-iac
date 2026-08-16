variable "subscription_id" {
  description = "The subscription ID where the BankCompliance AI workload resources will be deployed (Apps-prod)."
  type        = string
}

variable "location" {
  description = "The Azure region for main resources."
  type        = string
  default     = "centralindia"
}

variable "location_short" {
  description = "Short code for the main Azure region (e.g. cin)."
  type        = string
  default     = "cin"
}

variable "content_safety_location" {
  description = "The Azure region for Azure AI Content Safety (e.g. southeastasia for F0 SKU)."
  type        = string
  default     = "southeastasia"
}

variable "content_safety_location_short" {
  description = "Short code for Content Safety region (e.g. sea)."
  type        = string
  default     = "sea"
}

variable "swa_location" {
  description = "The Azure region for the Static Web App (e.g. eastus2 or centralindia)."
  type        = string
  default     = "eastus2"
}

variable "company_name" {
  description = "Company name for tagging."
  type        = string
  default     = "HappyTechies"
}

variable "project" {
  description = "Project code."
  type        = string
  default     = "ht"
}

variable "workload" {
  description = "Workload name (bankc for Bank Compliance AI)."
  type        = string
  default     = "bankc"
}

variable "environment" {
  description = "Environment code (e.g. p for production)."
  type        = string
  default     = "p"
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
  default     = "CC-AI-PLATFORM-01"
}

# ── Network Variables ─────────────────────────────────────────────────────────

variable "vnet_address_space" {
  description = "Address space for the spoke VNet."
  type        = list(string)
  default     = ["10.42.0.0/16"]
}

variable "aks_subnet_prefix" {
  description = "Subnet prefix for the AKS node pool."
  type        = string
  default     = "10.42.1.0/24"
}

variable "private_endpoints_subnet_prefix" {
  description = "Subnet prefix for private endpoints."
  type        = string
  default     = "10.42.2.0/24"
}

# ── Hub Lookup Variables ──────────────────────────────────────────────────────

variable "hub_subscription_id" {
  description = "Subscription ID of the Hub Network."
  type        = string
}

variable "hub_resource_group_name" {
  description = "Resource group name of the Hub Network."
  type        = string
  default     = "rg-ht-hub-p-cin-01"
}

variable "hub_vnet_name" {
  description = "VNet name of the Hub Network."
  type        = string
  default     = "vnet-ht-hub-p-cin-01"
}

# ── Shared Services Lookup Variables ──────────────────────────────────────────

variable "shared_subscription_id" {
  description = "Subscription ID of Shared Services."
  type        = string
}

variable "shared_resource_group_name" {
  description = "Resource group name of Shared Services."
  type        = string
  default     = "rg-ht-ss-p-cin-01"
}

variable "shared_law_name" {
  description = "Name of the central Log Analytics Workspace in Shared Services."
  type        = string
  default     = "law-ht-ss-p-cin-01"
}

variable "shared_apim_name" {
  description = "Name of the central API Management instance in Shared Services."
  type        = string
  default     = "apim-ht-ss-p-cin-01"
}

variable "shared_key_vault_name" {
  description = "Name of the central Key Vault in Shared Services."
  type        = string
  default     = "kv-ht-ss-p-cin-01"
}

# ── AKS Cluster Variables ─────────────────────────────────────────────────────

variable "aks_sku_tier" {
  description = "Pricing tier of the AKS cluster (Free for $0 control plane)."
  type        = string
  default     = "Free"
}

variable "aks_vm_size" {
  description = "VM size for the default AKS node pool (Standard_B4ms for 4 vCPU, 16GB RAM)."
  type        = string
  default     = "Standard_B4ms"
}

variable "aks_node_count" {
  description = "Number of worker nodes in the default node pool."
  type        = number
  default     = 1
}

variable "aks_os_disk_size_gb" {
  description = "OS disk size in GB (30GB fits ephemeral cache on Standard_B4ms)."
  type        = number
  default     = 30
}

variable "enable_azure_policy" {
  description = "Whether to enable Azure Policy (OPA Gatekeeper) add-on for banking compliance."
  type        = bool
  default     = true
}

# ── Custom Domain Variables ───────────────────────────────────────────────────

variable "custom_domain_name" {
  description = "Custom domain for the BankCompliance AI frontend."
  type        = string
  default     = "bank.mytaxbot.site"
}

variable "enable_custom_domain" {
  description = "Whether to bind the custom domain to the Static Web App (set to true after CNAME DNS record is added at registrar)."
  type        = bool
  default     = false
}

variable "enable_role_assignments" {
  description = "Whether to create RBAC role assignments for Managed Identities."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
