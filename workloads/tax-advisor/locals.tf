locals {
  tags = {
    Company     = var.company_name
    Project     = var.project
    Workload    = var.workload
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }
}
