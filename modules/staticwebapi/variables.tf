variable "resource_group_name" { type = string }
variable "environment" { type = string }
variable "location" { type = string }
variable "subscription_id" { type = string }
variable "tenant_id" { type = string }
variable "vnet_id" { type = string }
variable "subnet_map" { type = map(string) }
variable "key_vault_ref" {
  type = object({
    id   = string
    name = string
    uri  = string
  })
}
variable "naming_prefix" { type = string }
variable "instance_id" { type = string }
variable "tags" { type = map(string) }
