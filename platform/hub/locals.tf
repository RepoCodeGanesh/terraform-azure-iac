locals {
  tags = {
    Company     = var.company_name
    Environment = var.environment
    Project     = var.project
    Owner       = var.owner
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }
}
