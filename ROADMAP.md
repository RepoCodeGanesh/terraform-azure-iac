# Azure AI Landing Zone Roadmap & Implementation Plan

This document tracks the progress, completed milestones, and upcoming phases of the enterprise **Azure AI Landing Zone**, hosting **TaxBot India** (Serverless PaaS) and **BankCompliance AI** (Cloud-Native AKS).

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
| **Phase 10** | Enterprise Auditable Document Intelligence & LLMOps Platform | `app/bank-compliance/` & `.github/workflows/` | ✅ Completed |
| **Phase 11** | LLMOps Skill Bridge Phase 1 — Trivy CVE Scan, SecurityContext, KQL Workbook, Ollama SLM, Langfuse Tracing, Token Budget, MCP Server, AI Red-Team | `app/bank-compliance/` & `platform/shared-services/` | ✅ Completed |
| **Phase 12** | LLMOps Skill Bridge Phase 2 — LangGraph StateGraph Cyclic Multi-Agent Orchestrator (A1) & GPU vLLM Inference Benchmark (A3) | `app/bank-compliance/` & `workloads/bank-compliance-ai-aks/` | ✅ Completed |
| **Phase 13** | Enterprise Command & Governance Platform Refactoring, Air-Gapped SLM Alignment & Live Observability | `app/bank-compliance/` | ✅ Completed |

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
* [x] Package application as an atomic **Helm Chart** (`app/bank-compliance/chart/`) with Workload Identity, ConfigMaps, and LiteLLM secrets.
* [x] Implement **Continuous AI Evaluation & CI/CD Regression Quality Gate** (`evaluate.py` + `golden_dataset.jsonl`) blocking PRs on hallucination regressions.
* [x] Implement **Governed Semantic Vector Cache** in Qdrant with `corpus_version` invalidation & temporal/clause bypass (<10ms latency, $0 token cost).
* [x] Configure LiteLLM proxy gateway with dynamic environment variable expansion & Azure OpenAI (`gpt-5.4-nano`) + Google Gemini 2.0 Flash fallback.
* [x] Build and deploy React SPA frontend (`bank.mytaxbot.site`) on Azure Static Web Apps with Cloudflare DNS automation.
* [x] Integrate Prometheus & Grafana in-cluster monitoring stack (`monitoring` namespace) with ServiceMonitors.
* [x] Integrate Dual CI/CD (GitHub Actions + Azure DevOps) with DevSecOps SonarCloud SAST/SCA security scans.

---

## 🚀 Phase 10: Enterprise Auditable Document Intelligence & LLMOps Platform

### 📂 Track 1: Raw Regulatory Data Lake & Multi-Model Ingestion
* [x] **Raw Document Lake API:** Provisioned `DataLakeService` & `PDFIngestService` with automated SHA-256 integrity checks and document serving endpoints (`/api/v1/compliance/document/{id}`).
* [x] **Multi-Model AI Gateway:** Configured LiteLLM to route between **Google Gemini 2.0 Flash (Free Tier in AI Studio)** for heavy PDF parsing and **Azure OpenAI (`gpt-5.4-nano`)** for low-latency live chat.
* [x] **Layout-Aware Parsing:** Extract complex RBI tables, circular amendments, and page-level section maps into structured vector payloads.

### 🖥️ Track 2: Interactive Split-View Compliance Portal
* [x] **Split-Screen UI:** Left Pane (Conversational Copilot, PII shields, audit trail) + Right Pane (Interactive Regulatory Document & Clause Viewer `DocumentViewer.jsx`).
* [x] **Deep-Linked Interactive Citations:** Clicking any legal citation chip automatically navigates to the circular, scrolls to the referenced section, and highlights the corresponding clause.
* [x] **Multi-View Modes:** Supported 1-click toggling between Split Screen (50/50), Chat Only, and Clause Viewer Only.

### 🛡️ Track 3: Automated CI/CD LLMOps Quality & Safety Gates
* [x] **Automated RAG Evaluation in GitHub Actions:** Automated regression benchmarking on every Git Pull Request (`evaluate.py` + `golden_dataset.jsonl`).
* [x] **Triad Quality Gates:** Automated build enforcement of **Faithfulness $\ge 95\%$** (hallucination detector), **Answer Relevancy $\ge 90\%$**, and **Citation Integrity $\ge 4.0/5.0$**.
* [x] **Automated Jailbreak & Prompt Injection Testing:** Automated red-teaming tests running in the CI pipeline before deployment.
* [x] Execution Blueprint Document: [`docs/archive/RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md`](docs/archive/RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md)

---

## 🏆 Phase 11: LLMOps Skill Bridge Phase 1 — Lead AI Platform / LLMOps Architect Transition
**Goal:** Implement 8 additive LLMOps capabilities to bridge from Senior Azure DevOps Engineer to Lead AI Platform / LLMOps Architect (₹60L–₹85L+ CTC). **Total Cost: ₹0.**

### Track S: Security Hardening
* [x] **S3 — Trivy Container CVE Scan:** Added `aquasecurity/trivy-action@v0.36.0` after `docker push` in `.github/workflows/app-bank-compliance.yml`. SARIF output uploaded to GitHub Security Code Scanning. `exit-code: 0` (non-blocking). Added `security-events: write` + `actions: read` permissions.
* [x] **S1 (Safe Half) — Pod SecurityContext:** Added `runAsNonRoot: true`, `runAsUser: 1000`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]` to `k8s/backend-deployment.yaml`. `readOnlyRootFilesystem` intentionally omitted (breaks Qdrant + LiteLLM).

### Track O: Observability
* [x] **O2 — Azure Monitor Workbook (4 KQL Panels):** Replaced static `data_json` in `platform/shared-services/observability.tf` with 4 live KQL panels: AI Request Rate & Error Rate (5-min), Response Latency P50/P95/P99 (15-min), Qdrant Vector Search Activity (10-min barchart), Pod Status Timeline (bank-compliance namespace).
* [x] **O1 — Langfuse LLM Tracing:** Added `langfuse>=2.0.0` to `requirements.txt`. Created `backend/app/services/telemetry.py` with full graceful degradation (all SDK calls try/except). Added `bankc-langfuse-secret` secretRef (`optional: true`) to `backend-deployment.yaml`. Added `LANGFUSE_HOST` to `backend-configmap.yaml`.

### Track A: AI Capabilities
* [x] **A3 Phase 1 — Ollama CPU SLM (qwen2.5:0.5b):** Created `k8s/inference/private-slm-deployment.yaml` with `initContainer` that pre-pulls `qwen2.5:0.5b` into shared emptyDir volume before main Ollama server starts. Right-sized CPU requests to `10m` to avoid single-node scheduling deadlocks. Service `private-slm-inference:11434` live and verified.
* [x] **A2 — FastMCP Regulatory Search Server:** Created `backend/app/services/mcp_server.py` with FastMCP exposing `search_rbi_regulations(query, top_k)` and `list_regulatory_domains()` tools. Created `k8s/inference/mcp-deployment.yaml` (ClusterIP `bankc-mcp-server:8080`, SSE transport, explicit binding to `0.0.0.0:8080`). Added `fastmcp>=0.1.0` to `requirements.txt`.

### Track G: Governance
* [x] **G2 — AI Token Budget Circuit Breaker:** Added in-memory daily token counter (`_TOKEN_BUDGET_DAILY=500000`, auto-resets UTC midnight) to `orchestrator.py` & `orchestrator_v2.py`. Pre-flight check blocks requests when budget exhausted with user-friendly message. Added `DAILY_TOKEN_BUDGET: "500000"` to `backend-configmap.yaml`.

### Track S5: AI Red-Teaming
* [x] **S5 — AI Red-Team Assessment:** Created `scripts/red_team/run_pyrit.py` with 10 attack patterns across 6 categories (Jailbreak, Prompt Injection, Domain Evasion, Hallucination Induction, Context Poisoning, Obfuscation). Supports `--mode dry-run` (documentation) and `--mode live` (HTTP testing). Created `docs/ai-red-team-report.md` — full assessment documenting 4-layer defence-in-depth with 100% interception rate.

---

## 🏆 Phase 12: LLMOps Skill Bridge Phase 2 — LangGraph StateGraph & GPU vLLM Architecture
**Goal:** Implement advanced LLMOps architectural capabilities (LangGraph StateGraph cyclic reflection agent + Sovereign GPU vLLM benchmark).

### Track A1: LangGraph Multi-Agent StateGraph
* [x] **A1 — Cyclic StateGraph Orchestrator (`orchestrator_v2.py`):**
  - Created `app/bank-compliance/backend/app/services/agents/orchestrator_v2.py` implementing `StateGraph(AgentExecutionState)`.
  - Micro-agent nodes: `supervisor_node`, `retriever_node`, `auditor_node` (statutory reflection critic), `synthesizer_node` (LiteLLM multi-model fallback), `greeting_node`, `out_of_scope_node`.
  - Reflection loop: Conditional edge on auditor evaluation verdict (loops back to retriever if validation fails, max 2 iterations).
  - Production resilience: Integrated G2 token budget circuit breaker pre-flight check and graceful degradation fallback to `MultiAgentOrchestrator`.
  - Dual REST routing: Mounted `/api/v2` router prefix in `main.py` and dual endpoints `/compliance/query/v2` & `/v2/compliance/query` in `routes.py`.
  - Dependency: Added `langgraph>=0.2.0,<1.0.0` to `requirements.txt`.
  - Live Validation: Verified `/api/v2/compliance/query` returning HTTP 200 with 3 verified citations on live AKS cluster.

### Track A3 Phase 2: Sovereign GPU vLLM Inference Tier
* [x] **A3 Phase 2 — On-Demand GPU Node Pool & vLLM Benchmark:**
  - Added `enable_gpu_node_pool` boolean variable and `azurerm_kubernetes_cluster_node_pool "gpu"` in `workloads/bank-compliance-ai-aks/aks_cluster.tf` (`Standard_NC4as_T4_v3` Spot, `sku=gpu:NoSchedule` taint, ₹0 default).
  - Created `app/bank-compliance/k8s/inference/vllm-benchmark.yaml`: Kubernetes Deployment & Service running vLLM OpenAI API server with GPU acceleration and resource limits.
  - Created `scripts/benchmark_vllm.py`: Automated benchmarking harness measuring TTFT, tokens/sec, and latency percentiles (P50/P95/P99).
  - Benchmark findings (`docs/benchmark/vllm_benchmark_results.json`): GPU vLLM achieves **5.88x higher throughput** (142.8 vs 24.3 tokens/s) and **85.1% lower TTFT** (42.6ms vs 285ms) compared to CPU SLM at ₹35 one-time cost.

---

## 🏛️ Phase 13: Enterprise Web Refactoring, Sovereign SLM Alignment & Command/Governance Center
* [x] **5-Pillar Enterprise Architecture:**
  - Refactored `App.jsx` and `index.css` to deliver an uncluttered, modern fintech interface with 5 dedicated command pillars:
    1. 💬 **Regulatory Copilot:** Split-screen interactive chat with dynamic citation illumination against official RBI Master Directions.
    2. ⚡ **Command Center (`CommandCenter.jsx`):** Real-time fleet topology (APIM, LiteLLM, Private SLM, Qdrant), interactive sub-second execution pipeline visualizer, and infrastructure health controls.
    3. 🛡️ **Governance Center (`GovernanceCenter.jsx`):** DPDP Act 2023 real-time PII sanitization ledger, 3-Layer vector centroid sieve telemetry ($S \ge 0.030$), RBI Master Directions coverage matrix, and 1-click cryptographic audit attestation certificate generator.
    4. 📊 **Feasible Live Monitoring (`GenAIOpsDashboard.jsx`):** Native observability querying backend `/healthz`, `/compliance/stats`, and Prometheus telemetry for latency decomposition (TTFT, Vector search, LLM generation) and FinOps semantic cache savings ($94.2\%$).
    5. 📜 **Policy Redline Studio (`RedlineStudio.jsx`):** Automated clause-by-clause contract auditing diffing bank agreements against RBI IT Governance norms.
* [x] **Sovereign SLM Air-Gapped Pipeline & Trace Alignment:**
  - Resolved model mismatch: When Sovereign In-Cluster SLM is selected, execution traces strictly report local in-memory centroid sieve, internal Qdrant retrieval, air-gapped deterministic ground-truth validation, and in-cluster Qwen 2.5 (0.5B) synthesis.
  - Eliminated external Gemini calls during Sovereign mode for zero external cloud egress.
  - Model-scoped semantic vector cache (`semantic_cache.py` & `routes.py`) preventing cross-contamination between public cloud and sovereign SLM responses.
* [x] **Resource Optimization & Cluster Health:**
  - Scaled `vllm-benchmark-inference` deployment to 0 replicas on CPU-only cluster, eliminating pending scheduler warnings while keeping active sovereign SLM (`private-slm-inference`) 1/1 Running.
* [x] **Kubernetes Daily Operations Runbook & Triage Standards:**
  - Codified [Platform Guide 13: Enterprise Kubernetes Daily Operations Runbook](docs/platform-guide/13-kubernetes-daily-operations-runbook.md) across 10 operational tiers (Auth, Health, Pod Lifecycle, Deep Diagnostics, Zero-Trust Port-Forwarding, Helm Release Recovery, FinOps Scaling, Secrets/Storage, Networking, and 5-minute Emergency Triage).
  - Synchronized command cheatsheets into `app/bank-compliance/README.md` and documentation hubs.

---

## 🏛️ Architectural Decisions & Interview Talking Points

| Item | Status | Strategic / Interview Justification |
|:---|:---|:---|
| **S2 — NetworkPolicy** | Documented | Topology mapped: `backend ➔ qdrant:6333`, `backend ➔ litellm:4000`, `litellm ➔ external AI endpoints`. In enterprise banking, enforce deny-by-default with explicit allow egress rules. |
| **G1 — OPA Gatekeeper** | Concept Live | `azure_policy_enabled = true` is active on AKS; Gatekeeper admission controller webhook is live. In enterprise, add ConstraintTemplates for registry allowlists and `runAsNonRoot` enforcement. |
| **S1 (ReadOnlyRootFS)** | Omitted | Intentionally skipped `readOnlyRootFilesystem: true` because it breaks Qdrant local write buffers and LiteLLM socket logging. Non-root user 1000 + drop ALL capabilities provides full CIS compliance without runtime crashes. |
| **FinOps Teardown** | Verified | Strict declarative destruction (`terraform destroy -var-file="prod.tfvars" -auto-approve`) of `rg-ht-bankc-p-cin-01`. State cleanly preserved in `sthtbootpcin01`; 0 active cloud cost when idle. |

---

## 🎖️ Updated Master Resume Headline & Executive Profile (Post Phase 12)

```text
Lead Enterprise AI Platform & LLMOps Architect
Azure (AKS • LiteLLM • Qdrant • vLLM) | LangGraph | Langfuse | FastMCP | Terraform | Trivy | Red-Teaming
9+ years Experience | CKA | AZ-400 | AZ-305 | HashiCorp Terraform Certified
Production Workloads: https://bank.mytaxbot.site | https://www.mytaxbot.site
```

### 💼 Executive Summary & Core Competencies
* **Architectural Specialization:** Enterprise Cloud-Native Landing Zones (CAF), Multi-Agent LLMOps Orchestration, Sovereign In-Cluster SLM Inference, Zero-Trust DevSecOps, and FinOps Autonomous Metering.
* **Cloud & AI Tech Stack:** Azure (AKS, APIM, Key Vault, Monitor, Entra ID WIF), Terraform (Policy-as-Code, Terratest), Kubernetes (KEDA, CSI Storage, Ingress-NGINX), LangGraph (StateGraph Cyclic Multi-Agent), LiteLLM (Proxy Router, Fallback Chains), Qdrant (Hybrid Vector Lake), Ollama / vLLM, Langfuse, FastMCP, Trivy, Checkov, GitHub Actions CI/CD.

---

### 🚀 Production Enterprise Platform Engineering Accomplishments

#### 1. Cloud-Native Banking Regulatory Copilot & LLMOps Engine (BankCompliance AI)
* **Multi-Agent StateGraph Architecture:** Engineered an autonomous 4-tier regulatory copilot using **LangGraph StateGraph** coordinating **Supervisor Agent** (intent routing & guardrails), **Retriever Agent** (hybrid vector search over 24+ RBI Master Directions in Qdrant), **Auditor Agent** (chain-of-thought cyclic reflection & hallucination audit), and **Synthesizer Agent** (statutory legal grounding).
* **Multi-Cloud LLM Routing & In-Cluster Sovereign SLM:** Implemented LiteLLM enterprise routing with dynamic least-busy load balancing across **Google Gemini 2.0 Flash / Flash-Lite ($0 tier)** and **Groq LPU (500+ tok/s)** as primary synthesis, with automatic fallback to **Azure OpenAI (gpt-5.4-nano)** and in-cluster sovereign SLM **Qwen2.5-0.5B** on CPU via Ollama (zero API egress cost, 100% air-gapped compliance).
* **GenAIOps Command Center & Live Telemetry:** Built enterprise observability using **Langfuse OpenTelemetry tracing**, Prometheus fast-instrumentation, and Azure Monitor KQL workbooks tracking P50/P95/P99 latency waterfalls, token budgets (UTC circuit breaker), and Ragas Triad evaluation scores (**4.68/5.0 Groundedness, 4.92/5.0 Citation Integrity, 100% Security Pass Rate**).
* **FinOps Semantic Caching & Zero-Cost Architecture:** Implemented in-memory Euclidean distance vector semantic caching delivering **94.2% cache hit rate**, sub-10ms query responses, and cumulative token savings ($48.65+ per 1,400 queries). Sized AKS with KEDA scale-to-zero and Spot GPU node pools for an idle platform spend of **₹0 / month**.
* **Automated Policy & Contract Redline Studio:** Architected automated clause-by-clause statutory gap analysis diffing vendor agreements (e.g. SOW, SLAs, cloud hosting terms) against RBI IT Governance (`RBI/2023-24/108`) with one-click cryptographic audit attestation for Chief Compliance Officers.

#### 2. Enterprise Cloud Adoption Framework (CAF) Multi-Subscription Landing Zone
* **Management Hierarchy:** Architected 4-subscription enterprise landing zone under `HappieTechies-root-MG` comprising `platform/governance` (Azure Policy-as-Code), `platform/bootstrap` (remote state blob storage, Key Vault), `platform/hub` (Azure Firewall, Bastion, Virtual Network Gateway), `platform/shared-services` (APIM, Log Analytics Workspace), and `workloads/` (`tax-advisor`, `bank-compliance-ai-aks`).
* **Zero-Trust CI/CD & Workload Identity Federation (WIF):** Eliminated static cloud credentials across all GitHub Actions pipelines using Entra ID OIDC federated credentials, automated Checkov IaC security gates, Trivy container CVE scanning (SARIF integration), and dynamic UAMI client ID resolution.
