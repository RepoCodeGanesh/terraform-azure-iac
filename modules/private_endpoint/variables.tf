variable "name" {
  description = "Private endpoint name"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the private endpoint"
  type        = string
}

variable "virtual_network_id" {
  description = "Virtual network ID for the DNS link"
  type        = string
}

variable "private_connection_resource_id" {
  description = "Resource ID to connect to"
  type        = string
}

variable "subresource_names" {
  description = "Private link subresource names"
  type        = list(string)
}

variable "private_dns_zone_name" {
  description = "Private DNS zone name"
  type        = string
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
}
