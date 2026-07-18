variable "hub_rg_name" {
  type        = string
  description = "Existing dev hub resource group."
}

variable "hub_storage_account" {
  type        = string
  description = "Existing dev hub storage account."
}

variable "key_vault_name" {
  type        = string
  description = "Existing dev hub Key Vault."
}
