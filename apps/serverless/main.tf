data "azurerm_resource_group" "this" {
  name = var.resource_group_name
}

locals {
  plan_name     = substr(lower(replace("${var.naming_prefix}-asp-fn-${var.instance_id}", "_", "-")), 0, 60)
  function_name = substr(lower(replace("${var.naming_prefix}-func-${var.instance_id}", "_", "-")), 0, 60)
}

module "plan" {
  source  = "Azure/avm-res-web-serverfarm/azurerm"
  version = "2.0.6"

  name      = local.plan_name
  location  = var.location
  os_type   = "Linux"
  parent_id = data.azurerm_resource_group.this.id
  sku_name  = "Y1"
  tags      = var.tags
}

module "function_app" {
  source  = "Azure/avm-res-web-site/azurerm"
  version = "0.22.0"

  name                     = local.function_name
  location                 = var.location
  parent_id                = data.azurerm_resource_group.this.id
  service_plan_resource_id = module.plan.resource_id
  kind                     = "functionapp"
  https_only               = true
  tags                     = var.tags
}
