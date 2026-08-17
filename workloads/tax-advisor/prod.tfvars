# ==============================================================================
# Workload: TaxBot India Production Environment Configuration
# Target: Apps-prod Subscription (f4ffefe1-d689-4059-969c-ccc73e2a11d4)
# ==============================================================================

# ── Subscription & Region ───────────────────────────────────────────────────
subscription_id = "f4ffefe1-d689-4059-969c-ccc73e2a11d4"
location        = "centralindia"
location_short  = "cin"
swa_location    = "eastus2"

# ── CAF Naming Tokens ───────────────────────────────────────────────────────
project     = "ht"
workload    = "taxb"
environment = "p"
instance    = "01"

# ── Governance Tags ──────────────────────────────────────────────────────────
company_name = "HappyTechies"
owner        = "ai-platform-team"
cost_center  = "taxbot-india"

# ── Network Architecture ────────────────────────────────────────────────────
vnet_address_space              = ["10.41.0.0/16"]
app_subnet_prefix               = "10.41.1.0/24"
private_endpoints_subnet_prefix = "10.41.2.0/24"

# ── Hub Network Peering Lookups ──────────────────────────────────────────────
hub_subscription_id     = "3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b"
hub_resource_group_name = "rg-ht-hub-p-cin-01"
hub_vnet_name           = "vnet-ht-hub-p-cin-01"

# ── Shared Services Platform Lookups ─────────────────────────────────────────
shared_subscription_id     = "859a785c-bd38-402d-b595-1f44f40fb9bf"
shared_resource_group_name = "rg-ht-ss-p-cin-01"
shared_law_name            = "law-ht-ss-p-cin-01"
shared_apim_name           = "apim-ht-ss-p-cin-01"
shared_key_vault_name      = "kv-ht-ss-p-cin-01"
shared_openai_name         = "oai-ht-ss-p-eus-01"
shared_content_safety_name = "cs-ht-ss-p-sea-01"

# ── OpenAI Model Configuration ──────────────────────────────────────────────
openai_model_name    = "gpt-5.4-nano"
openai_model_version = "2026-03-17"

# ── RBAC Role Assignments ───────────────────────────────────────────────────
enable_role_assignments = true

# ── Monitoring & Alerting ───────────────────────────────────────────────────
alert_email_address        = "ganesank@mytaxbot.site"
enable_observability_agent = true


