variable "name" {
  description = "Name of the AKS cluster."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group where AKS will be deployed."
  type        = string
}

variable "location" {
  description = "Azure Region for the AKS cluster."
  type        = string
}

variable "dns_prefix" {
  description = "DNS prefix specified when creating the managed cluster."
  type        = string
}

variable "sku_tier" {
  description = "SKU Tier of the cluster (Free or Standard)."
  type        = string
  default     = "Free"
}

variable "subnet_id" {
  description = "Resource ID of the Subnet where the AKS nodes should be placed."
  type        = string
}

variable "vnet_id" {
  description = "Resource ID of the Spoke VNet (for Network Contributor role assignment)."
  type        = string
  default     = null
}

variable "enable_role_assignments" {
  description = "Whether to create role assignments for the AKS control plane identity."
  type        = bool
  default     = true
}

variable "enable_azure_policy" {
  description = "Whether Azure Policy add-on is enabled."
  type        = bool
  default     = false
}

variable "node_pool_name" {
  description = "Name of the default node pool."
  type        = string
  default     = "system"
}

variable "node_count" {
  description = "Initial number of nodes in default node pool."
  type        = number
  default     = 1
}

variable "vm_size" {
  description = "VM Size for default node pool."
  type        = string
  default     = "Standard_B2s"
}

variable "os_disk_type" {
  description = "OS Disk type for nodes (Ephemeral or Managed)."
  type        = string
  default     = "Ephemeral"
}

variable "os_disk_size_gb" {
  description = "OS Disk size in GB."
  type        = number
  default     = 30
}

variable "pod_cidr" {
  description = "CIDR for pods when Azure CNI overlay is used."
  type        = string
  default     = "10.244.0.0/16"
}

variable "service_cidr" {
  description = "CIDR for kubernetes services."
  type        = string
  default     = "172.16.0.0/16"
}

variable "dns_service_ip" {
  description = "IP address within service_cidr for CoreDNS."
  type        = string
  default     = "172.16.0.10"
}

variable "log_analytics_workspace_id" {
  description = "Resource ID of the Log Analytics Workspace for OMS Agent and cluster diagnostics."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to assign to the AKS cluster."
  type        = map(string)
  default     = {}
}
