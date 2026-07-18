output "primary_endpoint" {
  value = module.container_group.fqdn
}

output "function_endpoint" {
  value = null
}

output "connection_strings" {
  sensitive = true
  value     = {}
}

output "container_fqdn" {
  value = module.container_group.fqdn
}

output "resource_ids" {
  value = {
    container_group = module.container_group.resource_id
  }
}

output "normalized_names" {
  value = {
    container_group = local.name
    dns_label       = local.dns_label
  }
}
