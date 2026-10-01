# ==============================================================================
# AMBA Learning Lab: Azure Monitor Baseline Alerts for Storage Accounts
# Architecture: Cloud Adoption Framework (CAF) Policy-Driven Governance
# Target: Exclusively scoped to Bootstrap Subscription (7689ad81-71ba-481b-a17c-e1b6be61bab1)
# ==============================================================================

# ─── 1. AMBA Storage Account Availability Policy Definition ────────────────────
# Defined at the Root Management Group level so it follows CAF Enterprise standards,
# but only assigned to the Bootstrap subscription to test without impacting other workloads.

resource "azurerm_policy_definition" "amba_storage_availability" {
  name                = "amba-storage-availability"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "AMBA - Storage Account Availability Metric Alert"
  description         = "AMBA baseline: Automatically deploys a Sev 1 metric alert via DeployIfNotExists if Storage Account availability drops below 99%."
  management_group_id = "/providers/Microsoft.Management/managementGroups/${var.root_management_group_id}"

  metadata = jsonencode({
    category = "Monitoring"
    version  = "1.0.0"
    source   = "Azure Monitor Baseline Alerts (AMBA)"
  })

  parameters = jsonencode({
    effect = {
      type          = "String"
      defaultValue  = "DeployIfNotExists"
      allowedValues = ["DeployIfNotExists", "AuditIfNotExists", "Disabled"]
      metadata = {
        displayName = "Effect"
        description = "Enable or disable the execution of the policy"
      }
    }
    actionGroupId = {
      type = "String"
      metadata = {
        displayName = "Action Group ID"
        description = "The resource ID of the Action Group to notify when the alert fires"
      }
    }
    threshold = {
      type         = "Integer"
      defaultValue = 99
      metadata = {
        displayName = "Availability Threshold (%)"
        description = "The percentage below which an alert is triggered (default: 99)"
      }
    }
  })

  policy_rule = jsonencode({
    if = {
      field  = "type"
      equals = "Microsoft.Storage/storageAccounts"
    }
    then = {
      effect = "[parameters('effect')]"
      details = {
        type = "Microsoft.Insights/metricAlerts"
        name = "[concat(field('name'), '-Availability')]"
        existenceCondition = {
          allOf = [
            {
              field  = "Microsoft.Insights/metricAlerts/enabled"
              equals = "true"
            }
          ]
        }
        roleDefinitionIds = [
          "/providers/Microsoft.Authorization/roleDefinitions/749f88d5-cbae-40b8-b33c-38c9296bc3c0", # Monitoring Contributor
          "/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c"  # Contributor
        ]
        deployment = {
          properties = {
            mode = "incremental"
            template = {
              "$schema"      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
              contentVersion = "1.0.0.0"
              parameters = {
                storageAccountName = {
                  type = "string"
                }
                actionGroupId = {
                  type = "string"
                }
                threshold = {
                  type         = "int"
                  defaultValue = 99
                }
              }
              resources = [
                {
                  type       = "Microsoft.Insights/metricAlerts"
                  apiVersion = "2018-03-01"
                  name       = "[concat(parameters('storageAccountName'), '-Availability')]"
                  location   = "global"
                  tags = {
                    Environment = "p"
                    ManagedBy   = "AMBA"
                  }
                  properties = {
                    description  = "AMBA Baseline: Storage Account Availability is below threshold"
                    severity     = 1
                    enabled      = true
                    autoMitigate = true
                    scopes = [
                      "[resourceId('Microsoft.Storage/storageAccounts', parameters('storageAccountName'))]"
                    ]
                    evaluationFrequency = "PT5M"
                    windowSize          = "PT5M"
                    criteria = {
                      "odata.type" = "Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria"
                      allOf = [
                        {
                          name                 = "StorageAvailability"
                          criterionType        = "StaticThresholdCriterion"
                          metricNamespace      = "Microsoft.Storage/storageAccounts"
                          metricName           = "Availability"
                          operator             = "LessThan"
                          threshold            = "[parameters('threshold')]"
                          timeAggregation      = "Average"
                          skipMetricValidation = false
                        }
                      ]
                    }
                    actions = [
                      {
                        actionGroupId = "[parameters('actionGroupId')]"
                      }
                    ]
                  }
                }
              ]
            }
            parameters = {
              storageAccountName = {
                value = "[field('name')]"
              }
              actionGroupId = {
                value = "[parameters('actionGroupId')]"
              }
              threshold = {
                value = "[parameters('threshold')]"
              }
            }
          }
        }
      }
    }
  })
}

# ─── 2. Assign Policy to Bootstrap Subscription ────────

resource "azurerm_subscription_policy_assignment" "amba_storage_bootstrap" {
  provider             = azurerm.bootstrap
  name                 = "amba-storage-boot"
  display_name         = "AMBA Storage Baseline - Bootstrap (Learning Lab)"
  description          = "AMBA Metric Alert policy scoped exclusively to Bootstrap subscription (sthtbootpcin01)."
  subscription_id      = "/subscriptions/${var.bootstrap_subscription_id}"
  policy_definition_id = azurerm_policy_definition.amba_storage_availability.id
  location             = var.location

  identity {
    type = "SystemAssigned"
  }

  parameters = jsonencode({
    actionGroupId = {
      value = var.shared_services_action_group_id
    }
    threshold = {
      value = 99
    }
    effect = {
      value = "DeployIfNotExists"
    }
  })
}

# ─── 3. Managed Identity Role Assignments for Policy Remediation ──────────────
# DeployIfNotExists requires the Policy SystemAssigned Identity to have permission
# to deploy the Microsoft.Insights/metricAlerts resource inside the resource group.

resource "azurerm_role_assignment" "amba_policy_monitoring_contributor" {
  provider             = azurerm.bootstrap
  scope                = "/subscriptions/${var.bootstrap_subscription_id}"
  role_definition_name = "Monitoring Contributor"
  principal_id         = azurerm_subscription_policy_assignment.amba_storage_bootstrap.identity[0].principal_id
}

resource "azurerm_role_assignment" "amba_policy_contributor" {
  provider             = azurerm.bootstrap
  scope                = "/subscriptions/${var.bootstrap_subscription_id}"
  role_definition_name = "Contributor"
  principal_id         = azurerm_subscription_policy_assignment.amba_storage_bootstrap.identity[0].principal_id
}
