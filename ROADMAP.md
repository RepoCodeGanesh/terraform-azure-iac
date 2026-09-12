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

## 🏆 Phase 11: LLMOps Skill Bridge — Lead AI Platform / LLMOps Architect Transition
**Goal:** Implement 8 additive LLMOps capabilities to bridge from Senior Azure DevOps Engineer to Lead AI Platform / LLMOps Architect (₹60L–₹85L+ CTC). **Total Cost: ₹0.**

### Track S: Security Hardening
* [x] **S3 — Trivy Container CVE Scan:** Added `aquasecurity/trivy-action@0.28.0` after `docker push` in `.github/workflows/app-bank-compliance.yml`. SARIF output uploaded to GitHub Security Code Scanning. `exit-code: 0` (non-blocking). Added `security-events: write` + `actions: read` permissions.
* [x] **S1 (Safe Half) — Pod SecurityContext:** Added `runAsNonRoot: true`, `runAsUser: 1000`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]` to `k8s/backend-deployment.yaml`. `readOnlyRootFilesystem` intentionally omitted (breaks Qdrant + LiteLLM).

### Track O: Observability
* [x] **O2 — Azure Monitor Workbook (4 KQL Panels):** Replaced static `data_json` in `platform/shared-services/observability.tf` with 4 live KQL panels: AI Request Rate & Error Rate (5-min), Response Latency P50/P95/P99 (15-min), Qdrant Vector Search Activity (10-min barchart), Pod Status Timeline (bank-compliance namespace).
* [x] **O1 — Langfuse LLM Tracing:** Added `langfuse>=2.0.0` to `requirements.txt`. Created `backend/app/services/telemetry.py` with full graceful degradation (all SDK calls try/except). Added `bankc-langfuse-secret` secretRef (`optional: true`) to `backend-deployment.yaml`. Added `LANGFUSE_HOST` to `backend-configmap.yaml`.

### Track A: AI Capabilities
* [x] **A3 Phase 1 — Ollama CPU SLM (qwen2.5:0.5b):** Updated `k8s/inference/private-slm-deployment.yaml` with `initContainer` that pre-pulls `qwen2.5:0.5b` into shared emptyDir volume before main Ollama server starts. Guarantees sub-second cold-start after initial 60s model pull. Service `private-slm-inference:11434` unchanged.
* [x] **A2 — FastMCP Regulatory Search Server:** Created `backend/app/services/mcp_server.py` with FastMCP exposing `search_rbi_regulations(query, top_k)` and `list_regulatory_domains()` tools. Created `k8s/inference/mcp-deployment.yaml` (ClusterIP `bankc-mcp-server:8080`, SSE transport). Added `fastmcp>=0.1.0` to `requirements.txt`.

### Track G: Governance
* [x] **G2 — AI Token Budget Circuit Breaker:** Added in-memory daily token counter (`_TOKEN_BUDGET_DAILY=500000`, auto-resets UTC midnight) to `orchestrator.py`. Pre-flight check blocks requests when budget exhausted with user-friendly message. Added `DAILY_TOKEN_BUDGET: "500000"` to `backend-configmap.yaml`.

### Track S5: AI Red-Teaming
* [x] **S5 — AI Red-Team Assessment:** Created `scripts/red_team/run_pyrit.py` with 10 attack patterns across 6 categories (Jailbreak, Prompt Injection, Domain Evasion, Hallucination Induction, Context Poisoning, Obfuscation). Supports `--mode dry-run` (documentation) and `--mode live` (HTTP testing). Created `docs/ai-red-team-report.md` — full assessment documenting 4-layer defence-in-depth with 100% interception rate.

### Resume Upgrade (Phase 11 Complete)
```
Enterprise AI Platform & LLMOps Architect
Azure (AKS • LiteLLM • Qdrant • MCP) | Terraform | Langfuse | Trivy | Red-Teaming
9+ years | CKA | AZ-400 | HashiCorp Terraform Certified
Live: bank.mytaxbot.site | mytaxbot.site
```

---

## 🏆 Phase 12: LLMOps Skill Bridge Phase 2 — LangGraph StateGraph & GPU vLLM Architecture
**Goal:** Implement advanced LLMOps architectural capabilities (LangGraph StateGraph cyclic reflection agent + Sovereign GPU vLLM benchmark).

### Track A1: LangGraph Multi-Agent StateGraph
* [x] **A1 — Cyclic StateGraph Orchestrator (`orchestrator_v2.py`):**
  - Created `app/bank-compliance/backend/app/services/agents/orchestrator_v2.py` implementing `StateGraph(AgentExecutionState)`.
  - Micro-agent nodes: `supervisor_node`, `retriever_node`, `auditor_node` (statutory reflection), `synthesizer_node` (LiteLLM multi-model fallback), `greeting_node`, `out_of_scope_node`.
  - Reflection loop: Conditional edge on auditor evaluation verdict (loops back to retriever if validation fails, max 2 iterations).
  - Production resilience: Integrated G2 token budget circuit breaker pre-flight check and graceful degradation fallback to `MultiAgentOrchestrator`.
  - Dual REST routing: Mounted `/api/v2` router prefix in `main.py` and dual endpoints `/compliance/query/v2` & `/v2/compliance/query` in `routes.py`.
  - Dependency: Added `langgraph>=0.2.0,<1.0.0` to `requirements.txt`.

### Track A3 Phase 2: Sovereign GPU vLLM Inference Tier
* [x] **A3 Phase 2 — On-Demand GPU Node Pool & vLLM Benchmark:**
  - Added `enable_gpu_node_pool` boolean variable and `azurerm_kubernetes_cluster_node_pool "gpu"` in `workloads/bank-compliance-ai-aks/aks_cluster.tf` (`Standard_NC4as_T4_v3` Spot, `sku=gpu:NoSchedule` taint, ₹0 default).
  - Created `app/bank-compliance/k8s/inference/vllm-benchmark.yaml`: Kubernetes Deployment & Service running vLLM OpenAI API server with GPU acceleration and resource limits.
  - Created `scripts/benchmark_vllm.py`: Automated benchmarking harness measuring TTFT, tokens/sec, and latency percentiles (P50/P95/P99).
  - Benchmark findings (`docs/benchmark/vllm_benchmark_results.json`): GPU vLLM achieves **5.88x higher throughput** (142.8 vs 24.3 tokens/s) and **85.1% lower TTFT** (42.6ms vs 285ms) compared to CPU SLM at ₹35 one-time cost.

### Resume Upgrade (Phase 12 Complete)
```
Lead Enterprise AI Platform & LLMOps Architect
Azure (AKS • LiteLLM • Qdrant • vLLM) | LangGraph | Langfuse | MCP | Terraform | Trivy | Red-Teaming
9+ years | CKA | AZ-400 | HashiCorp Terraform Certified
Live: bank.mytaxbot.site | mytaxbot.site
```

