# ==============================================================================
# Platform: Shared Services Production Environment Configuration
# Target: Shared-services Subscription (859a785c-bd38-402d-b595-1f44f40fb9bf)
# ==============================================================================

# ── Subscription & Region ───────────────────────────────────────────────────
subscription_id = "859a785c-bd38-402d-b595-1f44f40fb9bf"
location        = "centralindia"
location_short  = "cin"

# ── CAF Naming Tokens ───────────────────────────────────────────────────────
project     = "ht"
workload    = "ss"
environment = "p"
instance    = "01"

# ── Governance Tags ──────────────────────────────────────────────────────────
company_name = "HappyTechies"
owner        = "platform-team"
cost_center  = "shared-services"

# ── Network Architecture ────────────────────────────────────────────────────
vnet_address_space              = ["10.30.0.0/16"]
management_subnet_prefix        = "10.30.0.0/24"
shared_services_subnet_prefix   = "10.30.1.0/24"
private_endpoints_subnet_prefix = "10.30.2.0/24"

# ── Hub Network Peering Lookups ──────────────────────────────────────────────
hub_subscription_id     = "3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b"
hub_resource_group_name = "rg-ht-hub-p-cin-01"
hub_vnet_name           = "vnet-ht-hub-p-cin-01"

# ── Platform Service Configurations ─────────────────────────────────────────
publisher_name               = "HappyTechies"
publisher_email              = "platform-team@contoso.com"
log_analytics_retention_days = 30
private_dns_zone_name        = "privatelink.vaultcore.azure.net"

# ── Shared AI Services (Multi-Region) ────────────────────────────────────────
content_safety_location       = "southeastasia"
content_safety_location_short = "sea"
openai_location               = "eastus"
openai_location_short         = "eus"
openai_model_name             = "gpt-5.4-nano"
openai_model_version          = "2026-03-17"
openai_model_capacity         = 10
