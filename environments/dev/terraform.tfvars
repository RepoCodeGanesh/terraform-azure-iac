environment = "dev"
location = "centralindia"
location_short = "cind"
hub_resource_group_name = "ht-centralindia-dev-rg-hub-01"
existing_key_vault_name = "ht-cind-dev-kv-hub-02"
existing_key_vault_secret_name = "INFRACOST-API-KEY"
tags = {
  environment = "dev"
  owner       = "platform"
  workload    = "hub-spoke-demo"
  managedBy   = "terraform"
}
