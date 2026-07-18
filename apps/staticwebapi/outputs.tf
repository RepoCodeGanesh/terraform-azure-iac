output "primary_endpoint" {
  value = module.static_site.resource_uri
}

output "function_endpoint" {
  value = null
}

output "connection_strings" {
  sensitive = true
  value     = {}
}

output "container_fqdn" {
  value = null
}

output "resource_ids" {
  value = {
    static_web_app = module.static_site.resource_id
  }
}

output "normalized_names" {
  value = {
    static_web_app = local.name
  }
}
