variable "resource_type" {
  description = "Azure resource type prefix (rg, kv, st, vnet, etc.)"
  type        = string
}

variable "project" {
  description = "Project short name"
  type        = string
}

variable "workload" {
  description = "Workload name (boot, hub, shared, app, ai, etc.)"
  type        = string
}

variable "environment" {
  description = "Deployment environment (d = Dev, p = Prod)"
  type        = string

  validation {
    condition     = contains(["d", "p"], var.environment)
    error_message = "Environment must be either 'd' or 'p'."
  }
}

variable "location_short" {
  description = "Azure region short code"
  type        = string
}

variable "instance" {
  description = "Instance number"
  type        = string
}