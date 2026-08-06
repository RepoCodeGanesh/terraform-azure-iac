variable "resource_group_name" {
  description = "Resource group name where the virtual network will be created."
  type        = string
}

variable "location" {
  description = "Azure region for the virtual network."
  type        = string
}

variable "vnet_name" {
  description = "Name of the virtual network."
  type        = string
}

variable "address_space" {
  description = "Address space for the hub virtual network."
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_names" {
  description = "Names of the subnets to create."
  type        = list(string)
  default     = ["AzureFirewallSubnet", "AzureBastionSubnet", "GatewaySubnet", "Management"]
}

variable "subnet_prefixes" {
  description = "CIDR prefixes for each subnet in the same order as subnet_names."
  type        = list(string)
  default     = ["10.0.0.0/26", "10.0.0.64/27", "10.0.0.96/27", "10.0.1.0/24"]
}

variable "tags" {
  description = "Tags to apply to the network resources."
  type        = map(string)
  default     = {}
}
