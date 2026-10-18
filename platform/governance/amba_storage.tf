# ==============================================================================
# AMBA Learning Lab: Azure Monitor Baseline Alerts for Storage Accounts
# Architecture: Cloud Adoption Framework (CAF) Policy-Driven Governance
# Target: Exclusively scoped to Bootstrap Subscription (7689ad81-71ba-481b-a17c-e1b6be61bab1)
# Cross-Subscription RBAC: Action Group Reader in Shared-Services (859a785c-bd38-402d-b595-1f44f40fb9bf)
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

# Cross-subscription permission: Policy Managed Identity needs read access
# to the centralized Action Group in Shared-services to link alert notifications.
resource "azurerm_role_assignment" "amba_policy_action_group_reader" {
  scope                = var.shared_services_action_group_id
  role_definition_name = "Monitoring Reader"
  principal_id         = azurerm_subscription_policy_assignment.amba_storage_bootstrap.identity[0].principal_id
}

# ==============================================================================
# AMBA Learning Lab — Part 2: Dynamic Threshold Alert (ML-Based Anomaly Detection)
# Metric: Storage Account Transactions (request volume anomaly)
# Why dynamic? Transaction counts vary by time-of-day & day-of-week — a static
# threshold would cause false alarms at off-peak hours or miss spikes at peak.
# Azure Monitor learns the normal baseline over 7–15 days and fires only when
# the metric deviates meaningfully from its own historical pattern.
# ==============================================================================

# ─── 4. AMBA Dynamic Threshold Policy Definition ────────────────────────────────
# Key differences vs static (Part 1):
#   criterionType  = "DynamicThresholdCriterion"  (vs StaticThresholdCriterion)
#   alertSensitivity = "Medium"                   (vs hardcoded threshold number)
#   odata.type     = MultipleResourceMultipleMetricCriteria (required for dynamic)
#   failingPeriods = consecutive windows that must breach before firing
#   NO threshold parameter — Azure learns it automatically

resource "azurerm_policy_definition" "amba_storage_transaction_anomaly" {
  name                = "amba-storage-transaction-anomaly"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "AMBA - Storage Account Transaction Anomaly Alert (Dynamic)"
  description         = "AMBA baseline: Deploys a Sev 2 dynamic metric alert via DeployIfNotExists when Storage Account transaction volume deviates abnormally from its ML-learned baseline."
  management_group_id = "/providers/Microsoft.Management/managementGroups/${var.root_management_group_id}"

  metadata = jsonencode({
    category = "Monitoring"
    version  = "1.0.0"
    source   = "Azure Monitor Baseline Alerts (AMBA) - Dynamic Learning Lab"
  })

  parameters = jsonencode({
    effect = {
      type         = "String"
      defaultValue = "DeployIfNotExists"
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
        description = "The resource ID of the Action Group to notify when the anomaly alert fires"
      }
    }
    # alertSensitivity controls how tight the ML band is:
    #   High   = fires on small deviations (more noise, fewer missed anomalies)
    #   Medium = balanced (recommended default)
    #   Low    = fires only on large deviations (quieter, may miss subtle spikes)
    alertSensitivity = {
      type         = "String"
      defaultValue = "Medium"
      allowedValues = ["High", "Medium", "Low"]
      metadata = {
        displayName = "Alert Sensitivity"
        description = "How sensitive the ML model is to deviations from the learned baseline"
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
        name = "[concat(field('name'), '-TransactionAnomaly')]"
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
                storageAccountName = { type = "string" }
                actionGroupId      = { type = "string" }
                alertSensitivity   = { type = "string", defaultValue = "Medium" }
              }
              resources = [
                {
                  type       = "Microsoft.Insights/metricAlerts"
                  apiVersion = "2018-03-01"
                  name       = "[concat(parameters('storageAccountName'), '-TransactionAnomaly')]"
                  location   = "global"
                  tags = {
                    Environment = "p"
                    ManagedBy   = "AMBA"
                    AlertType   = "Dynamic"
                  }
                  properties = {
                    description  = "AMBA Dynamic Baseline: Storage transaction volume is anomalous vs learned ML baseline"
                    severity     = 2
                    enabled      = true
                    autoMitigate = true
                    scopes = [
                      "[resourceId('Microsoft.Storage/storageAccounts', parameters('storageAccountName'))]"
                    ]
                    evaluationFrequency = "PT5M"
                    # Dynamic alerts need a wider window (PT1H) so the ML model
                    # has enough data points to compare against the historical band
                    windowSize = "PT1H"
                    criteria = {
                      # DYNAMIC requires MultipleResourceMultipleMetricCriteria
                      # (Static uses SingleResourceMultipleMetricCriteria)
                      "odata.type" = "Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria"
                      allOf = [
                        {
                          name             = "StorageTransactionAnomaly"
                          criterionType    = "DynamicThresholdCriterion"
                          metricNamespace  = "Microsoft.Storage/storageAccounts"
                          metricName       = "Transactions"
                          operator         = "GreaterOrLessThan" # fires on spike OR sudden drop
                          timeAggregation  = "Total"
                          # NO threshold value here — Azure learns it from history
                          alertSensitivity = "[parameters('alertSensitivity')]"
                          # failingPeriods: alert fires only if anomaly persists
                          # 3 out of 4 consecutive 5-min windows must breach the band
                          # prevents single-spike false alarms
                          failingPeriods = {
                            numberOfEvaluationPeriods = 4
                            minFailingPeriodsToAlert  = 3
                          }
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
              storageAccountName = { value = "[field('name')]" }
              actionGroupId      = { value = "[parameters('actionGroupId')]" }
              alertSensitivity   = { value = "[parameters('alertSensitivity')]" }
            }
          }
        }
      }
    }
  })
}

# ─── 5. Assign Dynamic Policy to Bootstrap Subscription ────────────────────────

resource "azurerm_subscription_policy_assignment" "amba_storage_transaction_anomaly_bootstrap" {
  provider             = azurerm.bootstrap
  name                 = "amba-storage-txn-boot"
  display_name         = "AMBA Storage Transaction Anomaly (Dynamic) - Bootstrap Learning Lab"
  description          = "Dynamic ML-based metric alert for Storage transaction anomalies, scoped to Bootstrap subscription."
  subscription_id      = "/subscriptions/${var.bootstrap_subscription_id}"
  policy_definition_id = azurerm_policy_definition.amba_storage_transaction_anomaly.id
  location             = var.location

  identity {
    type = "SystemAssigned"
  }

  parameters = jsonencode({
    actionGroupId = {
      value = var.shared_services_action_group_id
    }
    alertSensitivity = {
      value = "Medium"
    }
    effect = {
      value = "DeployIfNotExists"
    }
  })
}

# ─── 6. Role Assignments for Dynamic Policy Managed Identity ───────────────────

resource "azurerm_role_assignment" "amba_txn_policy_monitoring_contributor" {
  provider             = azurerm.bootstrap
  scope                = "/subscriptions/${var.bootstrap_subscription_id}"
  role_definition_name = "Monitoring Contributor"
  principal_id         = azurerm_subscription_policy_assignment.amba_storage_transaction_anomaly_bootstrap.identity[0].principal_id
}

resource "azurerm_role_assignment" "amba_txn_policy_contributor" {
  provider             = azurerm.bootstrap
  scope                = "/subscriptions/${var.bootstrap_subscription_id}"
  role_definition_name = "Contributor"
  principal_id         = azurerm_subscription_policy_assignment.amba_storage_transaction_anomaly_bootstrap.identity[0].principal_id
}

resource "azurerm_role_assignment" "amba_txn_policy_action_group_reader" {
  scope                = var.shared_services_action_group_id
  role_definition_name = "Monitoring Reader"
  principal_id         = azurerm_subscription_policy_assignment.amba_storage_transaction_anomaly_bootstrap.identity[0].principal_id
}

