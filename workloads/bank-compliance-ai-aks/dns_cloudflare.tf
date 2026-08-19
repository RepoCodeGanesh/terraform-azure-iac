# ==============================================================================
# Workload: BankCompliance AI — Cloudflare DNS & Custom Domain Tier
# Purpose: Automated DNS CNAME record creation via Cloudflare API & SWA SSL binding
# ==============================================================================

# ─── Cloudflare DNS: Auto-create CNAME Record for BankCompliance AI ──────────

resource "cloudflare_record" "bankc_cname" {
  zone_id = var.cloudflare_zone_id
  name    = "bank"
  content = module.bankc_frontend.default_host_name
  type    = "CNAME"
  proxied = false
  ttl     = 1

  depends_on = [module.bankc_frontend]
}

# ─── Custom Domain Validation & SSL Binding on Azure SWA ─────────────────────

resource "azurerm_static_web_app_custom_domain" "bankc_custom_domain" {
  count             = var.custom_domain_name != null ? 1 : 0
  static_web_app_id = module.bankc_frontend.id
  domain_name       = var.custom_domain_name
  validation_type   = "cname-delegation"

  depends_on = [
    module.bankc_frontend,
    cloudflare_record.bankc_cname
  ]
}
