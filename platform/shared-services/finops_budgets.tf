# ==============================================================================
# Platform: Shared Services — Pillar 1: FinOps Consumption Budgets ($0.00)
# Purpose: Hard cloud spend guardrails with automated email threshold alerts
# ==============================================================================

resource "azurerm_consumption_budget_subscription" "shared_services_budget" {
  name            = "budget-shared-services-p-cin-01"
  subscription_id = "/subscriptions/${var.subscription_id}"

  amount     = 15.00
  time_grain = "Monthly"

  time_period {
    start_date = formatdate("YYYY-MM-01'T'00:00:00Z", timestamp())
  }

  notification {
    enabled        = true
    threshold      = 70.0 # Alert at $10.50
    operator       = "GreaterThan"
    threshold_type = "Actual"

    contact_emails = [
      "richtextforganesh@outlook.com"
    ]
  }

  notification {
    enabled        = true
    threshold      = 90.0 # Alert at $13.50
    operator       = "GreaterThan"
    threshold_type = "Actual"

    contact_emails = [
      "richtextforganesh@outlook.com"
    ]
  }

  notification {
    enabled        = true
    threshold      = 100.0 # Alert at $15.00
    operator       = "GreaterThan"
    threshold_type = "Actual"

    contact_emails = [
      "richtextforganesh@outlook.com"
    ]
  }

  lifecycle {
    ignore_changes = [time_period]
  }
}
