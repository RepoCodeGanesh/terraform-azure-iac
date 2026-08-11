# Azure AI Landing Zone Roadmap & Implementation Plan

This document tracks the progress, status, and upcoming phases of building the enterprise **Azure AI Landing Zone**.

---

## 🚦 Phase Summary

| Phase | Description | Target Scope | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Remote Backend Storage & State Locking | `platform/bootstrap` | ✅ Completed |
| **Phase 2** | Central Hub Network & Subnet Topology | `platform/hub` | ✅ Completed |
| **Phase 3** | Shared Platform Services (APIM, LAW, DNS) | `platform/shared-services` | ✅ Completed |
| **Phase 4** | TaxBot India Workload (OpenAI, AI Search, Cosmos DB, Function App) | `workloads/tax-advisor` | ✅ Completed |
| **Phase 5** | Azure DevOps CI/CD & OIDC Workload Identity Federation | `pipelines/` | ✅ Completed |

---

## 🎯 Phase 1: Bootstrap Layer (`platform/bootstrap`)
* [x] Deploy Azure Storage Account (`sthtbootpcin01`) for remote `.tfstate` locking.
* [x] Configure Key Vault for bootstrap secrets.
* [x] Set Azure DevOps Service Connection `bootstrap` (Subscription: `7689ad81-71ba-481b-a17c-e1b6be61bab1`).

## 🌐 Phase 2: Hub Network Layer (`platform/hub`)
* [x] Deploy Hub VNet (`vnet-ht-hub-p-cin-01` / `10.0.0.0/16`).
* [x] Provision core subnets (`AzureFirewallSubnet`, `GatewaySubnet`, `AzureBastionSubnet`).
* [x] Set Azure DevOps Service Connection `hub-prod` (Subscription: `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b`).

## 🛠️ Phase 3: Shared Platform Services (`platform/shared-services`)
* [x] Deploy Log Analytics Workspace (`law-ht-ss-p-cin-01`) for central monitoring & AI telemetry.
* [x] Deploy API Management Gateway (`apim-ht-ss-p-cin-01`, SKU: `Consumption`) for prompt rate-limiting & CORS protection.
* [x] Deploy Private DNS Zones for internal service resolution.
* [x] Set Azure DevOps Service Connection `shared-services` (Subscription: `859a785c-bd38-402d-b595-1f44f40fb9bf`).

## 🤖 Phase 4: AI Workload Spoke (`workloads/tax-advisor`)
* [x] Deploy Spoke VNet (`10.41.0.0/16`) and peer with Hub VNet (`vnet-ht-hub-p-cin-01`).
* [x] Deploy Azure Cognitive Services / Azure OpenAI account (`oai-ht-taxb-p-eus-01` with `gpt-5.4-nano`).
* [x] Deploy Azure AI Search (`srch-ht-taxb-p-cin-01`) & Cosmos DB (`cosmos-ht-taxb-p-cin-01`).
* [x] Deploy Linux Function App (`func-ht-taxb-p-cin-01`) & Static Web App (`stapp-ht-taxb-p-cin-01` on `www.mytaxbot.site`).
* [x] Wire System Managed Identities & RBAC.
* [x] Set Azure DevOps Service Connection `app-prod` (Subscription: `f4ffefe1-d689-4059-969c-ccc73e2a11d4`, Workload Identity federation).

## 🔄 Phase 5: Automated CI/CD Pipelines (`pipelines/`)
* [x] Create multi-stage validation (`validate.yml`, `plan.yml`, `apply.yml`).
* [x] Configure pipeline triggers for `platform/bootstrap`, `platform/hub`, `platform/shared-services`, `workloads/tax-advisor`.
* [x] Wire `azure-cicd-tax-advisor.yml` & `azure-cicd-app-tax-advisor.yml` with `app-prod` service connection.
* [x] Execute end-to-end automated deployment test via Azure DevOps.
