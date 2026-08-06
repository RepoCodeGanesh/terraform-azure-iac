output "id" {
  description = "Resource ID of the Search Service."
  value       = module.search_service.resource_id
}

output "name" {
  description = "Name of the Search Service."
  value       = var.name
}

output "endpoint" {
  description = "Primary endpoint URL of the Search Service."
  value       = "https://${var.name}.search.windows.net"
}
