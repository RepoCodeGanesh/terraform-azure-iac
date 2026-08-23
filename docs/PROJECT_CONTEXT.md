# Project Context & Architecture

This is the canonical source of truth for the **Enterprise Azure AI Landing Zone Monorepo**, hosting infrastructure and application code for **TaxBot India** (Serverless PaaS) and **BankCompliance AI** (Cloud-Native AKS).

---

## 🎯 Repository Goal

Provision an enterprise-style Azure AI Landing Zone using Terraform and Dual CI/CD (Azure DevOps & GitHub Actions), following Microsoft Cloud Adoption Framework (CAF) patterns while maintaining low running costs with serverless and scale-to-zero architectures.

Core outcomes:
- Build enterprise-grade Azure DevOps and Terraform IaC practices.
- Provide a resilient, multi-subscription AI platform for Azure OpenAI, LiteLLM Multi-Model Gateway, APIM security, private networking, and AI Search / Qdrant RAG workloads.
- Host **TaxBot India (AI Income Tax Advisor)** on Serverless PaaS ([www.mytaxbot.site](https://www.mytaxbot.site)).
- Host **BankCompliance AI Copilot** on AKS Free Tier ([bank.mytaxbot.site](https://bank.mytaxbot.site)).
- Maintain near-zero idle cost using low-cost SKUs: APIM `Consumption_0`, Functions `Consumption Y1`, AKS Free Tier on Ephemeral OS with auto-shutdown, Qdrant on 4GB CSI disk, and Cosmos DB Serverless Free Tier.

---

## 🏗️ Architectural Topology

```
                  ┌─────────────────────────────────────────┐
                  │       Dual CI/CD (ADO & GHA WIF)        │
                  └────────────────────┬────────────────────┘
                                       │ (Workload Identity Federation)
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                            Azure Subscriptions                            │
 ├───────────────────┬───────────────────┬───────────────────┬───────────────┤
 │     Bootstrap     │     Hub-prod      │  Shared-services  │   Apps-prod   │
 │   7689ad81-...    │   3eb8cc01-...    │   859a785c-...    │  f4ffefe1-... │
 ├───────────────────┼───────────────────┼───────────────────┼───────────────┤
 │ • Remote state    │ • Hub VNet        │ • Log Analytics   │ • Spoke 1:    │
 │   Storage Account │   (10.0.0.0/16)   │   (law-ht-ss...)  │   TaxBot PaaS │
 │   (sthtbootpcin01)│ • Azure Firewall  │ • APIM Gateway    │   (10.41.0/16)│
 │ • Key Vault       │   Subnet          │   (Consumption)   │ • Spoke 2:    │
 │   (kv-ht-boot...) │ • Bastion Subnet  │ • Shared Key Vault│   Bankc AKS   │
 │                   │ • Gateway Subnet  │   (kv-ht-ss...)   │   (10.42.0/16)│
 └───────────────────┴───────────────────┴───────────────────┴───────────────┘
```

---

## 🚀 Active Workload Portfolio

### Workload 1: TaxBot India (`workloads/tax-advisor` & `app/tax-advisor`)
* **Production Domain:** [https://www.mytaxbot.site](https://www.mytaxbot.site)
* **Architecture:** Serverless PaaS (Python Function App `func-ht-taxb-p-cin-01`, Azure OpenAI `gpt-5.4-nano`, Azure AI Search, Cosmos DB).
* **Resource Group:** `rg-ht-taxb-p-cin-01` (`Apps-prod`) with Spoke VNet `10.41.0.0/16`.
* **CI/CD:** `pipelines/azure-cicd-tax-advisor.yml` & `.github/workflows/workload-tax-advisor.yml`.

### Workload 2: BankCompliance AI (`workloads/bank-compliance-ai-aks` & `app/bank-compliance`)
* **Industry Sector:** RegTech (Regulatory Technology / BFSI)
* **Production Domain:** [https://bank.mytaxbot.site](https://bank.mytaxbot.site)
* **APIM Gateway Endpoint:** `https://apim-ht-ss-p-cin-01.azure-api.net/bankc`
* **Architecture Stack:**
  * **Frontend:** React Vite SPA with Split-Screen Regulatory Clause Viewer & Citation Chips.
  * **API Gateway:** Azure API Management (`apim-ht-ss-p-cin-01`) Consumption Tier for SSL offloading & CORS.
  * **Compute:** Azure Kubernetes Service (AKS Free Tier `aks-ht-bankc-p-cin-01` on `Standard_B4ms` 4 vCPUs).
  * **Multi-Agent State Graph Orchestrator:**
    * 🎯 **Supervisor / Planner:** `gemini-2.0-flash-lite` (Intent classification & query decomposition)
    * 🔍 **Retriever Agent:** Autonomous Qdrant hybrid vector search
    * 🧠 **Auditor / Reflection Agent:** `gemini-2.0-flash-thinking` (Chain-of-Thought statutory verification & anti-hallucination)
    * ✍️ **Synthesizer Agent:** `gemini-2.0-flash` with automatic cross-cloud failover to Azure OpenAI `gpt-5.4-nano`
  * **Vector Database:** Qdrant Vector DB on 4GB CSI Azure Managed Disk with Governed Semantic Caching.
  * **Governance & Safety:** DPDP Act PII Sanitizer & Statutory Abstention Shield for out-of-scope queries.
  * **GenAIOps Command Center:** Prometheus & Grafana 6-Pillar Operational Dashboard (UID: `bank-compliance-ai-overview`).
* **Resource Group:** `rg-ht-bankc-p-cin-01` (`Apps-prod`) with Spoke VNet `10.42.0.0/16` (Azure CNI Overlay `192.168.0.0/16`).
* **CI/CD:** Dual CI/CD Pipelines (`pipelines/azure-cicd-bank-compliance-aks.yml` & `.github/workflows/app-bank-compliance.yml`).

```mermaid
flowchart TD
    User([Compliance User / Auditor]) -->|HTTPS| Frontend["bank.mytaxbot.site (React SPA)"]
    Frontend -->|POST /api/v1/compliance/query| APIM["Azure APIM Gateway<br/>(apim-ht-ss-p-cin-01)"]
    APIM -->|LoadBalanced HTTP| Backend["FastAPI Backend Pod<br/>(bankc-backend:8000)"]

    subgraph MultiAgentStateGraph ["🧠 Multi-Agent State Graph Orchestrator"]
        PII["🛡️ DPDP PII Shield & Out-of-Scope Filter"]
        Cache{"⚡ Semantic Vector Cache"}
        Supervisor["🎯 Supervisor Agent<br/>(gemini-2.0-flash-lite)"]
        Retriever["🔍 Retriever Agent"]
        Auditor["🧠 Auditor / Reflection Agent<br/>(gemini-2.0-flash-thinking)"]
        Synthesizer["✍️ Synthesizer Agent<br/>(gemini-2.0-flash)"]
    end

    Backend --> PII
    PII --> Cache
    Cache -->|Cache Miss| Supervisor
    Supervisor --> Retriever
    Retriever -->|Tool Query| Qdrant[("Qdrant Vector DB<br/>4GB CSI Disk")]
    Qdrant --> Auditor
    Auditor -->|Reflection / Self-Correction| Retriever
    Auditor -->|Evidence Verified| Synthesizer
    
    subgraph AIGateway ["🌐 LiteLLM Multi-Model Gateway Proxy"]
        LiteLLM["LiteLLM Pod (:4000)"]
        GeminiFleet["Google Cloud Fleet<br/>(flash / flash-lite / thinking)"]
        AzureFailover["Azure OpenAI Service<br/>(gpt-5.4-nano)"]
    end

    Synthesizer --> LiteLLM
    Supervisor -.-> LiteLLM
    Auditor -.-> LiteLLM
    LiteLLM -->|Primary Tier| GeminiFleet
    LiteLLM -.->|Cross-Cloud DR Fallback| AzureFailover

    subgraph Observability ["📊 10/10 GenAIOps Command Center"]
        Prometheus["Prometheus Server"]
        Grafana["Grafana Dashboard<br/>(bank-compliance-ai-overview)"]
    end

    Backend -->|/metrics (Custom PII & RAGOps)| Prometheus
    LiteLLM -->|/metrics (Tokens, Spend, 429s)| Prometheus
    Prometheus --> Grafana
```

---

## 📚 Central Confluence Space
* **HappyTechies Cloud & AI Platform:** [https://happytechies.atlassian.net/wiki/spaces/HT/overview](https://happytechies.atlassian.net/wiki/spaces/HT/overview)

Current status:
- `platform/bootstrap`: complete.
- `platform/hub`: complete.
- `platform/shared-services`: complete (Key Vault with dynamic AI endpoint registry, APIM, Log Analytics, Content Safety, OpenAI live; RBAC Admin role assigned).
- `workloads/tax-advisor`: complete (Serverless Function App + Cosmos + AI Search + Cloudflare DNS `www.mytaxbot.site` automated).
- `workloads/bank-compliance-ai-aks`: complete (AKS `Standard_B4ms` + Spoke VNet + APIM Gateway + Cloudflare DNS `bank.mytaxbot.site` automated).
- `app/tax-advisor`: complete (React UI + Python backend + APIM rate limiting + custom domain live).
- `app/bank-compliance`: complete (React SPA + FastAPI backend + LiteLLM + Qdrant Vector DB live).
- `pipelines/`: active and verified across both GitHub Actions and Azure DevOps with dedicated OIDC federated credentials.
- `dns_automation`: 100% automated via Cloudflare Terraform provider across both workloads with 10s `time_sleep` buffer.

---

## 🔑 Subscription Map & Dual CI/CD Authentication (WIF)

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

| Scope | Subscription | Subscription ID | Azure DevOps Service Connection | GitHub Actions Secret | App Registration (Client ID & Object ID) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | `BOOTSTRAP_CLIENT_ID` | `DevOpsUniverse-Terraform- bootstrap`<br>App ID: `934ab83b-2f61-475e-bdbc-85c9eaed83e6`<br>Obj ID: `f3a1b19b-11b8-4e13-8499-7f83ea39547a` |
| **Hub Network** | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | `HUB_CLIENT_ID` | `DevOpsUniverse-Terraform- hub-prod`<br>App ID: `78960c14-26d2-4a0c-ab21-579c3030155e`<br>Obj ID: `14cfc7b4-c3a2-4994-9f5c-0ce4d8db0f57` |
| **Shared Services** | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | `SHARED_CLIENT_ID` | `DevOpsUniverse-Terraform-shared-services`<br>App ID: `580ffcfd-51ee-4dc3-9204-d03cb438ff82`<br>Obj ID: `c5a24473-2bad-41a7-b0b1-b79b94621252` |
| **Apps / AI Workloads** | `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | `APP_CLIENT_ID` | `DevOpsUniverse-Terraform-app-prod`<br>App ID: `99ab7987-3989-46c3-bae9-92279be16608`<br>Obj ID: `9630f661-27e7-42f0-8377-5565ba7db7cd` |

---

## 🌐 Network CIDR Architecture (Hub & Spoke)

* **Hub Network**: `10.0.0.0/16` (`platform/hub`)
  * `AzureFirewallSubnet`: `10.0.0.0/26`
  * `AzureBastionSubnet`: `10.0.0.64/27`
  * `GatewaySubnet`: `10.0.0.96/27`
* **Spoke 1 (TaxBot PaaS)**: `10.41.0.0/16` (`workloads/tax-advisor`)
  * `snet-app-integration`: `10.41.1.0/24` (Subnet delegation for Function App VNet integration)
  * `PrivateEndpoints`: `10.41.2.0/24` (Private Link endpoints for OpenAI & Storage)
* **Spoke 2 (BankCompliance AKS)**: `10.42.0.0/16` (`workloads/bank-compliance-ai-aks`)
  * `snet-aks-nodes`: `10.42.1.0/24` (AKS Node Pool subnet with Azure CNI Overlay `192.168.0.0/16`)
  * `snet-ingress`: `10.42.2.0/24` (Internal/External Ingress LoadBalancer)

---

## 💰 Cost Optimization Matrix

| Resource Type | Resource Role | Selected SKU | Idle Running Cost |
| :--- | :--- | :--- | :--- |
| **API Management** | AI Prompt Gateway & Rate Limiting | `Consumption_0` | **$0 / month** |
| **App Service Plan** | Function App Host | `F1` (Free) / `B1` | **$0 – $13 / month** |
| **AKS Cluster** | BankCompliance Multi-Agent Host | `Free` tier (`Standard_B4ms` Ephemeral OS) | **$0 idle** (~₹25/day active) |
| **Container Storage** | Qdrant Vector DB Persistent Disk | Azure Managed Disk CSI (`4Gi`) | **~$0.15 / month** (₹12/mo) |
| **Log Analytics** | Central Application Telemetry | `PerGB2018` (30-day retention) | Pay-as-you-go |
| **Storage Account** | Terraform `.tfstate` & Functions | `Standard_LRS` | Pennies / month |
| **Cosmos DB** | Session Chat History Storage | Manual `400 RU/s` (Free Tier) | **$0 / month** |
| **Azure AI Content Safety** | Jailbreak Shield & PII Sanitizer | `F0` (5,000 calls/mo Free) | **$0 / month** |
| **Azure OpenAI** | LLM Inferences & Embeddings | Pay-As-You-Go (`S0` + `gpt-5.4-nano`) | Cap per token |

---

## 🔒 Terraform Multi-Root State Rules

Keep Terraform roots separate. Do not merge state:
- `platform/bootstrap`              → `sthtbootpcin01/tfstate/bootstrap/prod.tfstate`
- `platform/hub`                    → `sthtbootpcin01/tfstate/hub/prod.tfstate`
- `platform/shared-services`        → `sthtbootpcin01/tfstate/shared-services/prod.tfstate`
- `workloads/tax-advisor`           → `sthtbootpcin01/tfstate/workloads/tax-advisor/prod.tfstate`
- `workloads/bank-compliance-ai-aks` → `sthtbootpcin01/tfstate/workloads/bank-compliance-ai-aks/prod.tfstate`

---

## 📚 CI/CD & Governance Guides

- **Master Documentation Index:** [docs/README.md](README.md)
- **Git Branching Strategy:** [docs/BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md)
- **Automated Versioning (SemVer) Guide:** [docs/AUTOMATED_VERSIONING_GUIDE.md](AUTOMATED_VERSIONING_GUIDE.md)
- **Reusable App Workflow Guide:** [docs/REUSABLE_APP_WORKFLOW_GUIDE.md](REUSABLE_APP_WORKFLOW_GUIDE.md)
- **BankCompliance Troubleshooting & Learnings:** [docs/BANK_COMPLIANCE_TROUBLESHOOTING_AND_LEARNINGS.md](BANK_COMPLIANCE_TROUBLESHOOTING_AND_LEARNINGS.md)
- **Raw Regulatory Lake & Split-Screen Plan (Phase 10):** [docs/RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md](RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md)
- **AKS Hybrid Observability Guide:** [docs/AKS_HYBRID_OBSERVABILITY_GUIDE.md](AKS_HYBRID_OBSERVABILITY_GUIDE.md)
- **Azure RAG Architectural Patterns Guide:** [docs/platform-guide/08-azure-rag-architectural-patterns.md](platform-guide/08-azure-rag-architectural-patterns.md)
- **Multi-Cloud AI Gateway & Fallback Guide:** [docs/platform-guide/09-multi-cloud-ai-gateway-and-fallback-guide.md](platform-guide/09-multi-cloud-ai-gateway-and-fallback-guide.md)
- **AI Engineering Roadmap & Gap Analysis Guide:** [docs/platform-guide/10-enterprise-ai-engineering-backlog-and-roadmap.md](platform-guide/10-enterprise-ai-engineering-backlog-and-roadmap.md)

---

## 🤖 Developer AI Tooling & Environment Context

* **AI Subscription:** **Google AI Plus** (India tier)
* **Primary AI Models & Capabilities:** Gemini Pro flagship models with high rate limits and long-context reasoning.
* **Integrated Tooling Ecosystem:** Antigravity IDE, NotebookLM (used for analyzing large regulatory PDFs, Master Directions, and Tax Acts), Google Workspace AI integrations, and 200 GB Google One cloud storage.


