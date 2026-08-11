locals {
  resource_group_name = "rg-${var.company}-${var.environment}-${var.workload}-${var.region_code}-${var.instance}"

  standard_tags = {
    Company     = var.company
    Environment = var.environment
    Project     = var.project
    Owner       = var.owner
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }

  merged_tags = merge(local.standard_tags, var.tags)
}

resource "azurerm_resource_group" "this" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.merged_tags
}
