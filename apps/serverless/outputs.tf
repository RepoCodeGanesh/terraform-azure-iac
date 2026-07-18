output "primary_endpoint" {
  value = module.function_app.resource_uri
}

output "function_endpoint" {
  value = module.function_app.resource_uri
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
    service_plan = module.plan.resource_id
    function_app = module.function_app.resource_id
  }
}

output "normalized_names" {
  value = {
    service_plan = local.plan_name
    function_app = local.function_name
  }
}
