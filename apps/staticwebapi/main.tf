locals {
  raw_name = lower(replace("${var.naming_prefix}-swa-${var.instance_id}", "_", "-"))
  name     = substr(local.raw_name, 0, 60)
}

module "static_site" {
  source  = "Azure/avm-res-web-staticsite/azurerm"
  version = "0.6.2"

  name                = local.name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_tier            = "Free"
  tags                = var.tags
}
