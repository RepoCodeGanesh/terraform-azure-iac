# Azure AI Landing Zone Architecture

This document details the architectural design, subscription hierarchy, network topology, and security standards for the **Azure AI Landing Zone**.

---

## 🏗️ Architectural Topology

```
                  ┌─────────────────────────────────────────┐
                  │          Azure DevOps Pipelines         │
                  └────────────────────┬────────────────────┘
                                       │ (Workload Identity Federation)
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                            Azure Subscriptions                            │
 ├───────────────────┬───────────────────┬───────────────────┬───────────────┤
 │     Bootstrap     │     Hub-prod      │  Shared-services  │   Apps-prod   │
 │   7689ad81-...    │   3eb8cc01-...    │   859a785c-...    │  f4ffefe1-... │
 ├───────────────────┼───────────────────┼───────────────────┼───────────────┤
 │ • Remote state    │ • Hub VNet        │ • Log Analytics   │ • Spoke VNet  │
 │   Storage Account │ • Azure Firewall  │ • APIM Gateway    │ • OpenAI API  │
 │   (sthtbootpcin01)│   Subnet          │   (Consumption)   │ • AI Search   │
 │ • Key Vault       │ • Bastion Subnet  │ • Private DNS     │ • Function App│
 └───────────────────┴───────────────────┴───────────────────┴───────────────┘
```

---

## 🔑 Subscriptions & Federated Service Connections (WIF)

| Tier / Scope | Azure Subscription Name | Subscription ID | Azure DevOps Service Connection | Workload Target |
| :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | Remote Terraform backend storage (`sthtbootpcin01`) |
| **Hub Network** | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | Hub VNet (`vnet-ht-hub-p-cin-01`) & central routing |
| **Shared Services** | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | Log Analytics, APIM Gateway, Private DNS Zones |
| **Apps (AI Workloads)**| `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | TaxBot India (`workloads/tax-advisor`), OpenAI, AI Search |

---

## 🌐 Network Architecture (Hub & Spoke)

* **Hub Network**: `10.0.0.0/16` (`platform/hub`)
  * `AzureFirewallSubnet`: `10.0.0.0/26`
  * `AzureBastionSubnet`: `10.0.0.64/27`
  * `GatewaySubnet`: `10.0.0.96/27`
* **Spoke Network**: `10.41.0.0/16` (`workloads/tax-advisor`)
  * `snet-app-integration`: `10.41.1.0/24` (Subnet delegation for Function App VNet integration)
  * `PrivateEndpoints`: `10.41.2.0/24` (Private Link endpoints for OpenAI & Storage)

---

## 💰 Cost Optimization Matrix

To maintain near zero idle running costs in learning and developer environments, SKUs are selected as follows:

| Resource Type | Resource Role | Selected SKU | Idle Cost |
| :--- | :--- | :--- | :--- |
| **API Management** | AI Prompt Gateway & Rate Limiting | `Consumption_0` | **$0 / month** |
| **App Service Plan** | Function App Host | `F1` (Free) / `B1` | **$0 – $13 / month** |
| **Log Analytics** | Application Insights & Telemetry | `PerGB2018` (30-day retention) | Pay-as-you-go |
| **Storage Account** | Terraform `.tfstate` & Functions | `Standard_LRS` | Pennies / month |
| **Azure OpenAI** | LLM Inferences & Embeddings | Pay-As-You-Go | Cap per token |

---

## 🚀 Deployment Sequence

1. **`platform/bootstrap`**: Provisions remote backend state storage account and Key Vault.
2. **`platform/hub`**: Provisions central Hub VNet and routing subnets.
3. **`platform/shared-services`**: Provisions Log Analytics, APIM Gateway, and DNS zones.
4. **`workloads/tax-advisor`**: Provisions spoke VNet, peers to Hub VNet, deploys OpenAI, AI Search, Cosmos DB, and Function App host.
