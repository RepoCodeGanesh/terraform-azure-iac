# ==============================================================================
# Platform: Hub Production Environment Configuration
# Target: Hub-prod Subscription (3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b)
# ==============================================================================

# ── Subscription & Region ───────────────────────────────────────────────────
subscription_id = "3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b"
location        = "centralindia"
location_short  = "cin"

# ── CAF Naming Tokens ───────────────────────────────────────────────────────
project     = "ht"
workload    = "hub"
environment = "p"
instance    = "01"

# ── Governance Tags ──────────────────────────────────────────────────────────
company_name = "HappyTechies"
owner        = "platform-team"
cost_center  = "shared-services"

# ── Network Architecture ────────────────────────────────────────────────────
vnet_address_space       = ["10.0.0.0/16"]
firewall_subnet_prefix   = "10.0.0.0/26"
bastion_subnet_prefix    = "10.0.0.64/27"
gateway_subnet_prefix    = "10.0.0.96/27"
management_subnet_prefix = "10.0.1.0/24"
