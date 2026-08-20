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
| **Phase 8** | FinOps Cost Alerts & Logging Diagnostic Streamline | AI Workloads & Shared Services | ✅ Completed |
| **Phase 9** | BankCompliance AI Copilot on AKS (LiteLLM, Qdrant, Full RAG) | `workloads/bank-compliance-ai-aks` & `app/bank-compliance/` | ✅ Completed |
| **Phase 10** | *[Next]* Enterprise Auditable Document Intelligence & LLMOps Platform | `app/bank-compliance/` & `.github/workflows/` | 📋 Planned |

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
* [x] Deploy Shared Key Vault (`kv-ht-ss-p-cin-01`) with dynamic AI endpoint registry (`openai-endpoint`, `openai-api-key`, `content-safety-endpoint`).
* [x] Set Azure DevOps Service Connection `shared-services` (Subscription: `859a785c-bd38-402d-b595-1f44f40fb9bf`).

---

## 🤖 Phase 4: AI Workload Spoke (`workloads/tax-advisor`)
* [x] Deploy Spoke VNet (`10.41.0.0/16`) and peer with Hub VNet (`vnet-ht-hub-p-cin-01`).
* [x] Deploy Azure OpenAI account (`oai-ht-taxb-p-eus-01` with `gpt-5.4-nano`).
* [x] Deploy Azure AI Search (`srch-ht-taxb-p-cin-01`) & Cosmos DB (`cosmos-ht-taxb-p-cin-01`).
* [x] Deploy Linux Function App (`func-ht-taxb-p-cin-01`) & Static Web App (`stapp-ht-taxb-p-cin-01` on `www.mytaxbot.site`).
* [x] Codify zero-race Cloudflare DNS provider automation (`dns_cloudflare.tf`) with auto-managed SSL.
* [x] Wire System-Assigned Managed Identities & RBAC roles.
* [x] Set Azure DevOps Service Connection `app-prod` (Subscription: `f4ffefe1-d689-4059-969c-ccc73e2a11d4`).

---

## 🔄 Phase 5: Dual CI/CD Pipelines & WIF OIDC Authentication (`pipelines/` & `.github/`)
* [x] Create multi-stage IaC validation pipelines (Validate → Plan → Apply).
* [x] Configure dual authentication (Azure DevOps & GitHub Actions OIDC federation with dedicated `bank-compliance-prod` & `tax-advisor-prod` claims).
* [x] Implement reusable called workflows (`app-deploy-func.yml`, `app-deploy-swa.yml`, `app-sec-scan.yml`).
* [x] Add automated hourly AKS auto-shutdown workflow (`aks-auto-shutdown.yml`) for 24/7 idle VM cost optimization ($0/mo).

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

## 🏦 Phase 9: Banking Regulatory Compliance AI Copilot on AKS (`workloads/bank-compliance-ai-aks`)
* [x] Provision AKS Free Tier Cluster (`aks-ht-bankc-p-cin-01`, `sku_tier = "Free"`) in `workloads/bank-compliance-ai-aks`.
* [x] Deploy Qdrant Vector Database on AKS with 4GB Persistent CSI Disk (`managed-csi`) for RBI Master Direction HNSW indexing.
* [x] Configure LiteLLM proxy gateway with dynamic environment variable expansion & Azure OpenAI (`gpt-5.4-nano`).
* [x] Build and deploy React SPA frontend (`bank.mytaxbot.site`) on Azure Static Web Apps with Cloudflare DNS automation.
* [x] Integrate Prometheus & Grafana in-cluster monitoring stack (`monitoring` namespace) with ServiceMonitors.
* [x] Integrate Dual CI/CD (GitHub Actions + Azure DevOps) with DevSecOps SonarCloud SAST/SCA security scans.

---

## 🚀 Phase 10: Enterprise Auditable Document Intelligence & LLMOps Platform (Merged Next Milestone)

### 📂 Track 1: Raw Regulatory Data Lake & Multi-Model Ingestion
* [ ] **Raw PDF Lake:** Provision `rbi-raw-pdfs` container on Azure Blob Storage with automated SHA-256 integrity checks.
* [ ] **Multi-Model AI Gateway:** Configure LiteLLM to route between **Google Gemini 2.0 Flash (Free Tier in AI Studio)** for heavy 150-page PDF parsing and **Azure OpenAI (`gpt-5.4-nano`)** for low-latency live chat.
* [ ] **Layout-Aware Parsing:** Extract complex RBI tables, circular amendments, and page-level section maps into structured vector payloads.

### 🖥️ Track 2: Interactive Split-View Compliance Portal
* [ ] **Split-Screen UI:** Left Pane (Conversational Copilot, PII shields, audit trail) + Right Pane (Live PDF Document Viewer).
* [ ] **Deep-Linked Interactive Citations:** Clicking any legal citation (e.g. `[RBI Master Direction - Page 14]`) automatically scrolls the live PDF to Page 14 and highlights the corresponding clause.

### 🛡️ Track 3: Automated CI/CD LLMOps Quality & Safety Gates
* [ ] **Automated RAG Evaluation in GitHub Actions:** Automated **Ragas / TruLens** benchmarking on every Git Pull Request.
* [ ] **Triad Quality Gates:** Automated build failure if **Faithfulness < 95%** (hallucination detector), **Answer Relevancy < 90%**, or **Context Recall < 90%**.
* [ ] **Automated Jailbreak & Prompt Injection Testing:** Automated red-teaming tests running in the CI pipeline before production deployment.
* [ ] Architecture & Execution Document: [`docs/RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md`](docs/RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md)

