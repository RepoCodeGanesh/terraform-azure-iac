# ==============================================================================
# Platform: Bootstrap Production Environment Configuration
# Target: Bootstrap Subscription (7689ad81-71ba-481b-a17c-e1b6be61bab1)
# ==============================================================================

# ── Subscription & Region ───────────────────────────────────────────────────
subscription_id = "7689ad81-71ba-481b-a17c-e1b6be61bab1"
location        = "centralindia"
location_short  = "cin"

# ── CAF Naming Tokens ───────────────────────────────────────────────────────
project     = "ht"
workload    = "boot"
environment = "p"
instance    = "01"

# ── Governance Tags ──────────────────────────────────────────────────────────
company_name = "HappyTechies"
owner        = "platform-team"
cost_center  = "shared-services"

# ── Storage Configuration ───────────────────────────────────────────────────
tfstate_container_name = "tfstate"