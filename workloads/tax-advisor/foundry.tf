# ==============================================================================
# Workload: TaxBot India — Microsoft AI Foundry Tier
# Purpose: AI Foundry Hub, Model Deployments, and RBAC for Agent Service
# FinOps:  $0.00 idle cost (Serverless GlobalStandard pay-as-you-go)
# ==============================================================================

# ─── 1. AI Foundry Hub (Cognitive Services AIServices) ─────────────────────────

resource "azurerm_cognitive_account" "foundry_hub" {
  name                       = var.foundry_hub_name
  location                   = var.foundry_location
  resource_group_name        = azurerm_resource_group.tax_advisor.name
  kind                       = "AIServices"
  sku_name                   = "S0"
  custom_subdomain_name      = var.foundry_hub_name
  project_management_enabled = true

  identity {
    type = "SystemAssigned"
  }

  network_acls {
    default_action = "Allow"
    ip_rules       = []
  }

  tags = local.tags
}

# ─── 2. Serverless Model Deployment: gpt-5.4-mini ─────────────────────────────

resource "azurerm_cognitive_deployment" "foundry_gpt_mini" {
  name                 = "gpt-5.4-mini"
  cognitive_account_id = azurerm_cognitive_account.foundry_hub.id

  model {
    format  = "OpenAI"
    name    = "gpt-5.4-mini"
    version = "2026-03-17"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 10
  }
}

# ─── 3. Serverless Model Deployment: gpt-5.4-nano ─────────────────────────────

resource "azurerm_cognitive_deployment" "foundry_gpt_nano" {
  name                 = "gpt-5.4-nano"
  cognitive_account_id = azurerm_cognitive_account.foundry_hub.id

  model {
    format  = "OpenAI"
    name    = "gpt-5.4-nano"
    version = "2026-03-17"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 10
  }
}

# ─── 4. RBAC: Grant Function App Managed Identity access to Foundry Hub ────────

resource "azurerm_role_assignment" "func_foundry_openai_user" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = azurerm_cognitive_account.foundry_hub.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, azurerm_cognitive_account.foundry_hub]
}

resource "azurerm_role_assignment" "func_foundry_dev" {
  count                = var.enable_role_assignments ? 1 : 0
  scope                = azurerm_cognitive_account.foundry_hub.id
  role_definition_name = "Azure AI Developer"
  principal_id         = try(data.azurerm_linux_function_app.taxb_func.identity[0].principal_id, module.function_app.principal_id)
  depends_on           = [time_sleep.wait_for_func_identity, azurerm_cognitive_account.foundry_hub]
}
