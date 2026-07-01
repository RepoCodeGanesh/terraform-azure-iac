output "hub_resource_group_name" {
  value = module.hub_rg.name
}

output "hub_vnet_name" {
  value = module.hub_vnet.vnet_name
}

output "app1_storage_account_name" {
  value = module.app1_storage.name
}

output "app2_storage_account_name" {
  value = module.app2_storage.name
}

output "app1_webapp_name" {
  value = module.app1_appservice.name
}

output "app2_webapp_name" {
  value = module.app2_appservice.name
}

output "key_vault_name" {
  value = data.azurerm_key_vault.existing.name
}
