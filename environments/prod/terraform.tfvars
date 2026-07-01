environment = "prod"
location = "centralindia"
location_short = "cind"
hub_resource_group_name = "ht-centralindia-prod-rg-hub-01"
existing_key_vault_name = "ht-cind-prod-kv-hub-02"
existing_key_vault_secret_name = "INFRACOST-API-KEY"
tags = {
  environment = "prod"
  owner       = "platform"
  workload    = "hub-spoke-demo"
  managedBy   = "terraform"
}
