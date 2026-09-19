# 03. Workload 2: BankCompliance AI (Cloud-Native AKS Copilot)

* **Space:** `HappyTechies Cloud & AI Platform` -> `Workloads`
* **Live Domain:** [https://bank.mytaxbot.site](https://bank.mytaxbot.site)
* **Workload Code:** `bankc` (Resource Group: `rg-ht-bankc-p-cin-01`)
* **Infrastructure Root:** [`workloads/bank-compliance-ai-aks`](https://github.com/RepoCodeGanesh/terraform-azure-iac/tree/main/workloads/bank-compliance-ai-aks)
* **Application Path:** [`app/bank-compliance`](https://github.com/RepoCodeGanesh/terraform-azure-iac/tree/main/app/bank-compliance)
* **Status:** `ACTIVE / PROVISIONED`

---

## 1. Executive Summary & Problem Statement

Financial institutions process thousands of pages of central bank circulars, regulatory guidelines (RBI / SEC / Basel III), and compliance updates. **BankCompliance AI** is an enterprise-grade, auditable AI copilot built on **Azure Kubernetes Service (AKS)** that delivers sub-second interpretations of RBI Master Directions with exact clause-level legal citations.

---

## 2. Cloud-Native Kubernetes & Multi-Agent Architecture

```text
+--------------------------------------------------------------------------------------------------+
|              BANKCOMPLIANCE AI -- ENTERPRISE CLOUD-NATIVE KUBERNETES TOPOLOGY                    |
+--------------------------------------------------------------------------------------------------+

 [ Compliance Officers / Internal Auditors (https://bank.mytaxbot.site) ]
        |
        | 1. HTTPS / TLS 1.3
        v
 +---------------------------------------------------------------------------+
 | Azure Static Web Apps (Free Tier) | DNS: bank.mytaxbot.site               |
 | Features: Split-Screen Regulatory Viewer, Citation Deep-Linking, GenAIOps |
 +-------------------------------------+-------------------------------------+
                                       |
                                       | 2. HTTPS POST /api/v1/compliance/query
                                       v
 +---------------------------------------------------------------------------+
 | Azure APIM Gateway (Shared Services: apim-ht-ss-p-cin-01, Consumption)    |
 | * URL Rewrite: /bankc/api/v1/* -> /api/v1/*                               |
 | * Rate Limiting: 60 req/min per IP | CORS: https://bank.mytaxbot.site     |
 +-------------------------------------+-------------------------------------+
                                       |
                                       | 3. Forwarded HTTP (Port 80)
                                       v
 +---------------------------------------------------------------------------+
 | Azure Kubernetes Service (AKS Cluster: aks-ht-bankc-p-cin-01)             |
 | Node Pool: Standard_B4ms (Central India) | CNI Overlay: 192.168.0.0/16    |
 |                                                                           |
 | +-----------------------------------------------------------------------+ |
 | | Namespace: bank-compliance (Zero-Trust ClusterIP Isolation)           | |
 | |                                                                       | |
 | |  [ Service: bankc-backend-svc ] (Type: LoadBalancer, Port: 80)        | |
 | |          |                                                            | |
 | |          v                                                            | |
 | |  [ FastAPI Backend Pod ] --> (DPDP Act PII Sanitizer: PAN, Aadhaar)   | |
 | |          |                                                            | |
 | |          +--> [ Governed Semantic Cache ] (<10ms Cosine >= 0.90)      | |
 | |          |                                                            | |
 | |          +--> [ 4-Microagent State Graph Orchestrator ]               | |
 | |          |     +-- SupervisorAgent (Intent & Decomposition)           | |
 | |          |     +-- RetrieverAgent  (Tool caller on Qdrant)            | |
 | |          |     +-- AuditorAgent    (Reflection Critic Loop)           | |
 | |          |     \-- SynthesizerAgent(Grounded Legal Answer)            | |
 | |          |                                                            | |
 | |          +--> [ Qdrant Vector DB Pod ] (:6333)                        | |
 | |          |    (ClusterIP - 4GB Azure Managed CSI Disk, HNSW Index)    | |
 | |          |                                                            | |
 | |          \--> [ LiteLLM Gateway Proxy Pod ] (:4000)                   | |
 | |                     +-- Primary:   Google Gemini 2.0 Flash (Free)     | |
 | |                     +-- Failover:  Azure OpenAI gpt-5.4-nano (East US)| |
 | |                     \-- Sovereign: [ In-Cluster Private SLM ] (:11434)| |
 | |                                    (Qwen-2.5 / Phi-3 on CPU)          | |
 | +-----------------------------------------------------------------------+ |
 +---------------------------------------------------------------------------+
```

---

## 3. Key Architectural Decisions & Low-Level Specifications

| Dimension | Architectural Choice | Low-Level Specification & Rationale |
| :--- | :--- | :--- |
| **Compute Engine** | **AKS Free Tier (`Standard_B4ms`)** | 4 vCPUs, 16GB RAM, Ephemeral OS Disk. Zero control-plane management fee. |
| **Vector Storage** | **4GB Managed Disk (`managed-csi`)** | `StandardSSD_LRS` mounted to `/qdrant/data`. Preserves embeddings across cluster stops (~$0.15/mo). |
| **State Graph** | **4-Microagent Architecture** | Decoupled cognitive nodes with deterministic 3-layer vector centroid sieve (<3ms) and 2-iteration reflection loop. |
| **Semantic Cache** | **Governed Vector Cache** | In-memory + Qdrant similarity match (Cosine >= 0.90). Serves repeat queries in **8.4ms at $0.00 spend**. |
| **Fine-Tuning Engine**| **LoRA / PEFT Pipeline** | PyTorch + HuggingFace PEFT (r=16, alpha=32). Specialized on 1,915 synthetic RBI instruction pairs (+34.25% groundedness lift). |
| **Sovereign Inference**| **In-Cluster SLM Tier** | Local `ollama` pod hosting `qwen2.5:0.5b` on CPU. Zero external token egress for ultra-sensitive banking data. |
| **Telemetry & SRE** | **OpenTelemetry GenAI (v1.26+)** | Emits standard `gen_ai.system`, `gen_ai.usage.tokens`, and span latency breakdown across all micro-agents. |
| **Security & Privacy** | **DPDP Act PII Sanitizer** | Real-time regex + NER redacting PAN, Aadhaar, and credit card numbers prior to LLM processing. |

---

## 4. Master FinOps & Cost Matrix

| Component | Selected Configuration | Idle Cost (Cluster Stopped) | Active Daily Cost |
| :--- | :--- | :---: | :---: |
| **AKS Control Plane** | `sku_tier = "Free"` | **$0.00** | **$0.00** |
| **Compute Node Pool** | 1x `Standard_B4ms` (Ephemeral OS Disk) | **$0.00** | **~$0.30 / day** (~INR 25/day) |
| **Qdrant Storage** | 4GB Azure Managed Disk (`managed-csi`) | **~$0.15 / month** | **~$0.15 / month** (INR 12/mo) |
| **AI Content Safety** | `F0` Free Tier (5,000 calls/mo) | **$0.00** | **$0.00** |
| **Static Web App** | `Free` Tier (`bank.mytaxbot.site`) | **$0.00** | **$0.00** |
| **LoRA Fine-Tuning** | Local / GitHub Actions CPU Runner | **$0.00** | **$0.00** |
| **In-Cluster Private SLM**| Runs on existing AKS Node Pool | **$0.00** | **$0.00** |
| **TOTAL** | | **~$0.15 / month** | **~$0.15/mo + INR 25/day active** |
