locals {
  normalized_prefix = lower(replace(var.resource_group_prefix, "_", "-"))
  name_base         = "${local.normalized_prefix}-${var.environment}-${var.workspace}"
  name_hash         = substr(md5(local.name_base), 0, 3)

  storage_base_raw   = lower(replace(local.name_base, "-", ""))
  storage_base_short = substr(local.storage_base_raw, 0, 21)
  storage_account    = length(local.storage_base_raw) > 24 ? "${local.storage_base_short}${local.name_hash}" : local.storage_base_raw

  key_vault_base_raw   = lower(replace(local.name_base, "_", "-"))
  key_vault_base_short = substr(local.key_vault_base_raw, 0, 20)
  key_vault_name       = length(local.key_vault_base_raw) > 24 ? "${local.key_vault_base_short}-${local.name_hash}" : local.key_vault_base_raw

  spoke_rg_name   = "${local.name_base}-rg-spoke-01"
  spoke_vnet_name = "${local.name_base}-vnet-spoke-01"

  app_names = toset(["staticwebapi", "serverless", "securems"])
  selected_apps = {
    for name in local.app_names : name => name
    if contains(var.enabled_apps, name)
  }

  key_vault_ref = var.key_vault_name == "" ? null : {
    id   = data.azurerm_key_vault.hub[0].id
    name = data.azurerm_key_vault.hub[0].name
    uri  = data.azurerm_key_vault.hub[0].vault_uri
  }

  tags = merge({
    environment = var.environment
    workload    = "cind-learning"
    managed_by  = "terraform"
    repo        = "terraform-azure-iac"
  }, var.tags)
}
