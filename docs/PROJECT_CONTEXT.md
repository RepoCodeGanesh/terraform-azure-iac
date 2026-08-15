# Project Context & Architecture

This is the compact source of truth for the Azure AI Landing Zone & TaxBot India application repository.

---

## 🎯 Repository Goal

Provision an enterprise-style Azure AI Landing Zone using Terraform and Azure DevOps CI/CD, following Microsoft Cloud Adoption Framework patterns while keeping idle cost as close to zero as practical.

Core outcomes:
- Build hands-on Azure DevOps and Terraform IaC practice.
- Create a reusable AI platform foundation for Azure OpenAI, APIM gateway security, telemetry, private networking, and AI Search RAG workloads.
- Host **TaxBot India (AI Income Tax Advisor)** for FY 2026-27 (AY 2027-28).
- Use low-cost SKUs by default: APIM `Consumption`, Functions `Consumption Y1`, Log Analytics `PerGB2018`, Storage `Standard_LRS`, Key Vault `Standard`, Azure OpenAI `S0` with `gpt-5.4-nano`, and Cosmos DB `Serverless`.

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
 │ • Key Vault       │ • Bastion Subnet  │ • Key Vault       │ • Function App│
 └───────────────────┴───────────────────┴───────────────────┴───────────────┘
```

---

## 🚀 Active Workload Portfolio

### Workload 1: TaxBot India (`workloads/tax-advisor` & `app/tax-advisor`)
* **Production Domain:** [https://www.mytaxbot.site](https://www.mytaxbot.site)
* **Architecture:** Serverless PaaS (Python Function App `func-ht-taxb-p-cin-01`, Azure OpenAI `gpt-5.4-nano`, Azure AI Search, Cosmos DB).
* **Resource Group:** `rg-ht-taxb-p-cin-01` (`Apps-prod`) with Spoke VNet `10.41.0.0/16`.
* **CI/CD:** `pipelines/azure-cicd-tax-advisor.yml` & `.github/workflows/workload-tax-advisor.yml`.

### Workload 2: BankCompliance AI (`workloads/bank-compliance-ai-aks` & `bank-compliance-ai-app`)
* **Production Domain:** [https://bank.mytaxbot.site](https://bank.mytaxbot.site)
* **Architecture:** Cloud-Native Kubernetes (AKS Free Tier `aks-ht-bankc-p-cin-01`, LiteLLM Proxy Gateway, Qdrant Vector DB on 4GB CSI Managed Disk, KEDA Scale-to-Zero, DPDP PII Auto-Masking).
* **Resource Group:** `rg-ht-bankc-p-cin-01` (`Apps-prod`) with Spoke VNet `10.42.0.0/16` (Azure CNI Overlay `192.168.0.0/16`).
* **Sister Application Repository:** [`bank-compliance-ai-app`](https://github.com/RepoCodeGanesh/bank-compliance-ai-app) (Local: `c:\Users\RichT\OneDrive\Documents\Repos\bank-compliance-ai-app`)
* **CI/CD:** `pipelines/azure-cicd-bank-compliance-aks.yml` & `.github/workflows/workload-bank-compliance-aks.yml`.

---

## 📚 Central Confluence Space
* **HappyTechies Cloud & AI Platform:** [https://happytechies.atlassian.net/wiki/spaces/HT/overview](https://happytechies.atlassian.net/wiki/spaces/HT/overview)

Current status:
- `platform/bootstrap`: complete.
- `platform/hub`: complete.
- `platform/shared-services`: complete.
- `workloads/tax-advisor`: complete.
- `workloads/bank-compliance-ai-aks`: complete.
- `workloads/tax-advisor`: complete (IaC deployed & active).
- `app/tax-advisor`: complete (React UI + Python backend + APIM rate limiting + custom domain live).
- `pipelines/`: active and verified.

---

## 🔑 Subscription Map & Dual CI/CD Authentication (WIF)

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

| Scope | Subscription | Subscription ID | Azure DevOps Service Connection | GitHub Actions Secret | App Registration (Client ID) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | `BOOTSTRAP_CLIENT_ID` | `DevOpsUniverse-Terraform- bootstrap`<br>`934ab83b-2f61-475e-bdbc-85c9eaed83e6` |
| **Hub Network** | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | `HUB_CLIENT_ID` | `DevOpsUniverse-Terraform- hub-prod`<br>`78960c14-26d2-4a0c-ab21-579c3030155e` |
| **Shared Services** | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | `SHARED_CLIENT_ID` | `DevOpsUniverse-Terraform-shared-services`<br>`580ffcfd-51ee-4dc3-9204-d03cb438ff82` |
| **Apps / AI Workloads** | `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | `APP_CLIENT_ID` | `DevOpsUniverse-Terraform-app-prod`<br>`99ab7987-3989-46c3-bae9-92279be16608` |

---

## 🌐 Network CIDR Architecture (Hub & Spoke)

* **Hub Network**: `10.0.0.0/16` (`platform/hub`)
  * `AzureFirewallSubnet`: `10.0.0.0/26`
  * `AzureBastionSubnet`: `10.0.0.64/27`
  * `GatewaySubnet`: `10.0.0.96/27`
* **Spoke Network**: `10.41.0.0/16` (`workloads/tax-advisor`)
  * `snet-app-integration`: `10.41.1.0/24` (Subnet delegation for Function App VNet integration)
  * `PrivateEndpoints`: `10.41.2.0/24` (Private Link endpoints for OpenAI & Storage)

---

## 💰 Cost Optimization Matrix

| Resource Type | Resource Role | Selected SKU | Idle Running Cost |
| :--- | :--- | :--- | :--- |
| **API Management** | AI Prompt Gateway & Rate Limiting | `Consumption_0` | **$0 / month** |
| **App Service Plan** | Function App Host | `F1` (Free) / `B1` | **$0 – $13 / month** |
| **Log Analytics** | Application Insights & Telemetry | `PerGB2018` (30-day retention) | Pay-as-you-go |
| **Storage Account** | Terraform `.tfstate` & Functions | `Standard_LRS` | Pennies / month |
| **Cosmos DB** | Session Chat History Storage | Manual `400 RU/s` (Free Tier) | **$0 / month** |
| **Azure AI Content Safety** | Jailbreak Shield & PII Sanitizer | `F0` (5,000 calls/mo Free) | **$0 / month** |
| **Azure OpenAI** | LLM Inferences & Embeddings | Pay-As-You-Go (`S0` + `gpt-5.4-nano`) | Cap per token |

---

## 🔒 Terraform Multi-Root State Rules

Keep Terraform roots separate. Do not merge state:
- `platform/bootstrap`       → `sthtbootpcin01/tfstate/bootstrap/prod.tfstate`
- `platform/hub`             → `sthtbootpcin01/tfstate/hub/prod.tfstate`
- `platform/shared-services` → `sthtbootpcin01/tfstate/shared-services/prod.tfstate`
- `workloads/tax-advisor`    → `sthtbootpcin01/tfstate/workloads/tax-advisor/prod.tfstate`

---

## 📚 CI/CD & Governance Guides

- **Git Branching Strategy:** [docs/BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md)
- **Automated Versioning (SemVer) Guide:** [docs/AUTOMATED_VERSIONING_GUIDE.md](AUTOMATED_VERSIONING_GUIDE.md)
- **Reusable App Workflow Guide:** [docs/REUSABLE_APP_WORKFLOW_GUIDE.md](REUSABLE_APP_WORKFLOW_GUIDE.md)
- **Master Documentation Index:** [docs/README.md](README.md)
