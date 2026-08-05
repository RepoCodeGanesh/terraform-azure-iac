output "vnet_name" {
  description = "Virtual network name."
  value       = module.hub_vnet.vnet_name
}

output "vnet_id" {
  description = "Virtual network resource ID."
  value       = module.hub_vnet.vnet_id
}

output "subnet_ids" {
  description = "List of subnet resource IDs."
  value       = module.hub_vnet.vnet_subnets
}
