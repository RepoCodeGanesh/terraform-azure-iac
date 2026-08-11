variable "vnet_1_name" {
  description = "Name of the first virtual network."
  type        = string
}

variable "vnet_1_rg" {
  description = "Resource group name of the first virtual network."
  type        = string
}

variable "vnet_1_id" {
  description = "Resource ID of the first virtual network."
  type        = string
}

variable "vnet_2_name" {
  description = "Name of the second virtual network."
  type        = string
}

variable "vnet_2_rg" {
  description = "Resource group name of the second virtual network."
  type        = string
}

variable "vnet_2_id" {
  description = "Resource ID of the second virtual network."
  type        = string
}

variable "allow_virtual_network_access" {
  description = "Controls if the VMs in the remote virtual network can access VMs in the local virtual network."
  type        = bool
  default     = true
}

variable "allow_forwarded_traffic" {
  description = "Controls if forwarded traffic from VMs in the remote virtual network is allowed."
  type        = bool
  default     = true
}
