output "resource_group" {
  value = data.azurerm_resource_group.hub
}

output "storage_account_id" {
  value = data.azurerm_storage_account.hub_state.id
}

output "key_vault_ref" {
  value = {
    id   = data.azurerm_key_vault.hub.id
    name = data.azurerm_key_vault.hub.name
    uri  = data.azurerm_key_vault.hub.vault_uri
  }
}
