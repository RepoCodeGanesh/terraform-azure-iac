# Azure AI Landing Zone Roadmap & Implementation Plan

This document tracks the progress, completed milestones, and upcoming phases of the enterprise **Azure AI Landing Zone** and **TaxBot India** AI workload platform.

---

## 🚦 Phase Summary

| Phase | Description | Target Scope | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Remote Backend Storage & State Locking | `platform/bootstrap` | ✅ Completed |
| **Phase 2** | Central Hub Network & Subnet Topology | `platform/hub` | ✅ Completed |
| **Phase 3** | Shared Platform Services (APIM Gateway, LAW, Key Vault) | `platform/shared-services` | ✅ Completed |
| **Phase 4** | TaxBot India Workload (OpenAI, AI Search, Cosmos DB, Function App) | `workloads/tax-advisor` | ✅ Completed |
| **Phase 5** | Dual CI/CD Pipelines & WIF OIDC Authentication | `pipelines/` & `.github/` | ✅ Completed |
| **Phase 6** | DevSecOps SAST/SCA & Release Asset Distribution | `.github/workflows/` | ✅ Completed |
| **Phase 7** | Platform Visual Documentation & Incident Playbooks | `docs/platform-guide/` | ✅ Completed |
| **Phase 8** | *[Active]* FinOps Cost Alerts & RAG Vector Tuning | AI Workloads & Governance | 🔄 Planned |

---

## 🎯 Phase 1: Bootstrap Layer (`platform/bootstrap`)
* [x] Deploy Azure Storage Account (`sthtbootpcin01`) for remote `.tfstate` locking.
* [x] Configure Key Vault (`kv-ht-boot-p-cin-01`) for bootstrap secrets.
* [x] Set Azure DevOps Service Connection `bootstrap` (Subscription: `7689ad81-71ba-481b-a17c-e1b6be61bab1`).

---

## 🌐 Phase 2: Hub Network Layer (`platform/hub`)
* [x] Deploy Hub VNet (`vnet-ht-hub-p-cin-01` / `10.0.0.0/16`).
* [x] Provision core subnets (`AzureFirewallSubnet`, `GatewaySubnet`, `AzureBastionSubnet`).
* [x] Set Azure DevOps Service Connection `hub-prod` (Subscription: `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b`).

---

## 🛠️ Phase 3: Shared Platform Services (`platform/shared-services`)
* [x] Deploy Log Analytics Workspace (`law-ht-ss-p-cin-01`) for central monitoring & AI telemetry.
* [x] Deploy API Management Gateway (`apim-ht-ss-p-cin-01`, SKU: `Consumption`) for prompt rate-limiting & CORS protection.
* [x] Deploy Shared Key Vault (`kv-ht-ss-p-cin-01`) for deployment tokens.
* [x] Set Azure DevOps Service Connection `shared-services` (Subscription: `859a785c-bd38-402d-b595-1f44f40fb9bf`).

---

## 🤖 Phase 4: AI Workload Spoke (`workloads/tax-advisor`)
* [x] Deploy Spoke VNet (`10.41.0.0/16`) and peer with Hub VNet (`vnet-ht-hub-p-cin-01`).
* [x] Deploy Azure OpenAI account (`oai-ht-taxb-p-eus-01` with `gpt-5.4-nano`).
* [x] Deploy Azure AI Search (`srch-ht-taxb-p-cin-01`) & Cosmos DB (`cosmos-ht-taxb-p-cin-01`).
* [x] Deploy Linux Function App (`func-ht-taxb-p-cin-01`) & Static Web App (`stapp-ht-taxb-p-cin-01` on `www.mytaxbot.site`).
* [x] Wire System-Assigned Managed Identities & RBAC roles.
* [x] Set Azure DevOps Service Connection `app-prod` (Subscription: `f4ffefe1-d689-4059-969c-ccc73e2a11d4`).

---

## 🔄 Phase 5: Dual CI/CD Pipelines & WIF OIDC Authentication (`pipelines/` & `.github/`)
* [x] Create multi-stage IaC validation pipelines (Validate → Plan → Apply).
* [x] Configure dual authentication (Azure DevOps & GitHub Actions OIDC federation).
* [x] Implement reusable called workflows (`app-deploy-func.yml`, `app-deploy-swa.yml`, `app-sec-scan.yml`).
* [x] Execute end-to-end automated deployment tests across environments.

---

## 🛡️ Phase 6: DevSecOps SAST/SCA & Release Asset Distribution
* [x] Integrate SAST code analysis (`Bandit`), SCA dependency scanning (`pip-audit`, `npm audit`), and `SonarCloud` quality gates.
* [x] Implement automated Semantic Versioning (`v1.2.0`) via `github-tag-action`.
* [x] Configure automated GitHub Release publishing with attached compiled build artifacts (`functionapp.zip`).

---

## 📚 Phase 7: Platform Visual Documentation & Incident Playbooks
* [x] Convert legacy `.txt` platform documentation into a visual Markdown suite (`docs/platform-guide/`).
* [x] Add interactive Mermaid architecture diagrams, subscription maps, and sequence flows.
* [x] Build incident response playbooks for APIM 500, SWA CORS, statutory tax edge cases (80CCD(2), Rule 2A HRA), and TF locks.
* [x] Upgrade statutory RAG tax files in `app/tax-advisor/documents/` to structured Markdown (`.md`).

---

## 🚀 Phase 8: Upcoming Enhancements (Backlog)
* [ ] Implement FinOps automated cost anomaly alerts in Azure Monitor.
* [ ] Enhance Azure AI Search indexer with hybrid vector search and semantic ranker tuning.
* [ ] Add automated k6 / Locust load testing pipelines for APIM rate-limiting verification.
