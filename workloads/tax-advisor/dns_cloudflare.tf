# ==============================================================================
# Workload: TaxBot India — Cloudflare DNS & Custom Domain Tier
# Purpose: Automated DNS CNAME record creation via Cloudflare API & SWA SSL binding
# ==============================================================================

# ─── Cloudflare DNS: Auto-create CNAME Record for TaxBot India ──────────────

resource "cloudflare_record" "taxb_cname" {
  zone_id = var.cloudflare_zone_id
  name    = "www"
  content = module.taxb_frontend.default_host_name
  type    = "CNAME"
  proxied = false
  ttl     = 1

  depends_on = [module.taxb_frontend]
}

resource "cloudflare_record" "taxb_apex" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  content = module.taxb_frontend.default_host_name
  type    = "CNAME"
  proxied = false
  ttl     = 1

  depends_on = [module.taxb_frontend]
}

# ─── Wait 10s for Global DNS Edge Propagation (Prevents Race Conditions) ──────

resource "time_sleep" "wait_for_dns" {
  create_duration = "10s"

  depends_on = [cloudflare_record.taxb_cname]
}

# ─── Custom Domain Validation & SSL Binding on Azure SWA ─────────────────────

resource "azurerm_static_web_app_custom_domain" "taxb_custom_domain" {
  count             = var.custom_domain_name != null ? 1 : 0
  static_web_app_id = module.taxb_frontend.id
  domain_name       = var.custom_domain_name
  validation_type   = "cname-delegation"

  depends_on = [
    module.taxb_frontend,
    cloudflare_record.taxb_cname,
    time_sleep.wait_for_dns
  ]
}
