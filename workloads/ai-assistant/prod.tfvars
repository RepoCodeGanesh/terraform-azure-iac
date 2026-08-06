subscription_id                 = "f4ffefe1-d689-4059-969c-ccc73e2a11d4"
location                        = "centralindia"
location_short                  = "cin"
openai_location                 = "eastus"
openai_location_short           = "eus"
swa_location                    = "eastus2"
project                         = "ht"
workload                        = "dvob"
environment                     = "p"
instance                        = "01"
vnet_address_space              = ["10.40.0.0/16"]
app_subnet_prefix               = "10.40.1.0/24"
private_endpoints_subnet_prefix = "10.40.2.0/24"
hub_subscription_id             = "3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b"
hub_resource_group_name         = "rg-ht-hub-p-cin-01"
hub_vnet_name                   = "vnet-ht-hub-p-cin-01"
shared_subscription_id          = "859a785c-bd38-402d-b595-1f44f40fb9bf"
shared_resource_group_name      = "rg-ht-ss-p-cin-01"
shared_law_name                 = "law-ht-ss-p-cin-01"
shared_apim_name                = "apim-ht-ss-p-cin-01"

# OpenAI Model configuration
openai_model_name    = "gpt-5.4-nano"
openai_model_version = "2026-03-17"

# Set to false if Azure DevOps Service Principal lacks 'Microsoft.Authorization/roleAssignments/write' RBAC on Apps-prod subscription
enable_role_assignments = true


