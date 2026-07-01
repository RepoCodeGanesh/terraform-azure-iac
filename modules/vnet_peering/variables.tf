variable "name" {
  description = "Peering name"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group of the local virtual network"
  type        = string
}

variable "virtual_network_name" {
  description = "Name of the local virtual network"
  type        = string
}

variable "remote_virtual_network_id" {
  description = "Resource ID of the remote virtual network"
  type        = string
}
