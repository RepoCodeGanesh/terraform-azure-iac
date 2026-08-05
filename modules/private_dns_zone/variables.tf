variable "name" {
  description = "Private DNS Zone name."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group where the private DNS zone will be created."
  type        = string
}

variable "tags" {
  description = "Tags to apply to the private DNS zone."
  type        = map(string)
  default     = {}
}
