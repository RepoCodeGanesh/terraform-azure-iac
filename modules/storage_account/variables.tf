variable "name" {
  description = "Name of the Storage Account."
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group where the Storage Account will be created."
  type        = string
}

variable "location" {
  description = "Azure Region for the Storage Account."
  type        = string
}

variable "account_tier" {
  description = "Tier to use for this storage account."
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "Type of replication to use for this storage account (LRS, GRS, etc.)."
  type        = string
  default     = "LRS"
}

variable "account_kind" {
  description = "Kind of storage account (StorageV2, BlobStorage, etc.)."
  type        = string
  default     = "StorageV2"
}

variable "public_network_access_enabled" {
  description = "Whether public network access is enabled."
  type        = bool
  default     = true
}

variable "shared_access_key_enabled" {
  description = "Whether shared access keys (account keys) are enabled."
  type        = bool
  default     = true
}

variable "blob_retention_days" {
  description = "Number of days for blob delete retention policy."
  type        = number
  default     = 1
}

variable "container_retention_days" {
  description = "Number of days for container delete retention policy."
  type        = number
  default     = 1
}

variable "container_name" {
  description = "Optional container name to create inside the storage account."
  type        = string
  default     = null
}

variable "container_access_type" {
  description = "Access type for the optional container (private, blob, container)."
  type        = string
  default     = "private"
}

variable "tags" {
  description = "Tags to assign to the storage account."
  type        = map(string)
  default     = {}
}
