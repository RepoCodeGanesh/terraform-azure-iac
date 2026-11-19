output "name" {
  description = "Generated Azure resource name (for single resource_type)."
  value       = local.resource_name
}

output "names" {
  description = "Map of generated Azure resource names keyed by resource_type."
  value       = local.names
}