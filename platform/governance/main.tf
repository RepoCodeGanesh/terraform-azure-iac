# ==============================================================================
# Enterprise Azure Management Groups & Policy-as-Code (CAF Standard)
# HappyTechies Cloud & AI Platform
# ==============================================================================

# ─── 1. Enterprise Management Groups ──────────────────────────────────────────

resource "azurerm_management_group" "platform" {
  name                       = "mg-ht-platform"
  display_name               = "HappyTechies Platform"
  parent_management_group_id = "/providers/Microsoft.Management/managementGroups/${var.root_management_group_id}"

  subscription_ids = [
    "7689ad81-71ba-481b-a17c-e1b6be61bab1", # bootstrap
    "3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b", # Hub-prod
    "859a785c-bd38-402d-b595-1f44f40fb9bf"  # Shared-services
  ]
}

resource "azurerm_management_group" "landingzones" {
  name                       = "mg-ht-landingzones"
  display_name               = "HappyTechies Landing Zones"
  parent_management_group_id = "/providers/Microsoft.Management/managementGroups/${var.root_management_group_id}"

  subscription_ids = [
    "f4ffefe1-d689-4059-969c-ccc73e2a11d4"  # Apps-prod
  ]
}

# ─── 2. Enterprise Governance & Security Initiative (Policy Set) ─────────────

resource "azurerm_management_group_policy_set_definition" "enterprise_baseline" {
  name                 = "initiative-ht-enterprise-baseline"
  policy_type          = "Custom"
  display_name         = "HappyTechies Enterprise Governance Baseline"
  description          = "Enterprise Security, Tagging, Region, and Zero-Trust Guardrails across all Landing Zones."
  management_group_id  = "/providers/Microsoft.Management/managementGroups/${var.root_management_group_id}"

  # 1. Allowed Deployment Locations
  policy_definition_reference {
    policy_definition_id         = "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c"
    reference_id                 = "AllowedLocations"
    parameter_values = jsonencode({
      listOfAllowedLocations = {
        value = [
          "centralindia",
          "southindia",
          "westindia",
          "southeastasia", # AI Content Safety
          "eastus",        # Azure OpenAI
          "eastus2",
          "global"         # Front Door / Static Web Apps
        ]
      }
    })
  }

  # 2. Enforce HTTPS / Secure Transfer on Storage Accounts
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9"
    reference_id         = "StorageHttpsOnly"
  }

  # 3. Enforce HTTPS Only on App Services & Functions
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/a4af4a39-4135-47fb-b175-47fbdf85311d"
    reference_id         = "AppServiceHttpsOnly"
  }

  # 4. Enforce Key Vault Soft-Delete
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d"
    reference_id         = "KeyVaultSoftDelete"
  }

  # 5. Require 'Environment' Tag on Resources
  policy_definition_reference {
    policy_definition_id         = "/providers/Microsoft.Authorization/policyDefinitions/871b6d14-10aa-478d-b590-94f262ecfa99"
    reference_id                 = "RequireEnvironmentTag"
    parameter_values = jsonencode({
      tagName = {
        value = "Environment"
      }
    })
  }
}

# ─── 3. Assign Enterprise Initiative at Root Management Group ────────────────

resource "azurerm_management_group_policy_assignment" "baseline" {
  name                 = "ht-enterprise-baseline"
  management_group_id  = "/providers/Microsoft.Management/managementGroups/${var.root_management_group_id}"
  policy_definition_id = azurerm_management_group_policy_set_definition.enterprise_baseline.id
  display_name         = "HappyTechies Enterprise Guardrails"
  location             = var.location

  identity {
    type = "SystemAssigned"
  }
}
