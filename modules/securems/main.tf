locals {
  name      = substr(lower(replace("${var.naming_prefix}-aci-${var.instance_id}", "_", "-")), 0, 60)
  dns_label = substr(lower(replace("${var.naming_prefix}-aci-${var.instance_id}", "_", "")), 0, 63)
}

module "container_group" {
  source  = "Azure/avm-res-containerinstance-containergroup/azurerm"
  version = "0.2.0"

  name                = local.name
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  restart_policy      = "Always"
  dns_name_label      = local.dns_label
  tags                = var.tags

  exposed_ports = [
    {
      port     = 80
      protocol = "TCP"
    }
  ]

  containers = {
    app = {
      image  = "mcr.microsoft.com/azuredocs/aci-helloworld"
      cpu    = 0.5
      memory = 1
      ports = [
        {
          port     = 80
          protocol = "TCP"
        }
      ]
      volumes = {}
    }
  }
}
