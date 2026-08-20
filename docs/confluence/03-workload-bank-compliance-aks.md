# 🏦 Workload 2: BankCompliance AI (Cloud-Native AKS Banking Copilot)

* **Space:** `HappyTechies Cloud & AI Platform` $\rightarrow$ `Workloads`
* **Live Domain:** [https://bank.mytaxbot.site](https://bank.mytaxbot.site)
* **Workload Code:** `bankc` (Resource Group: `rg-ht-bankc-p-cin-01`)
* **Infrastructure Repo:** [`terraform-azure-iac`](https://github.com/RepoCodeGanesh/terraform-azure-iac) $\rightarrow$ `workloads/bank-compliance-ai-aks`
* **Application Repo:** [`bank-compliance-ai-app`](https://github.com/RepoCodeGanesh/bank-compliance-ai-app)
* **Status:** `ACTIVE / PROVISIONED`

---

## 🎯 1. Executive Summary & Problem Statement

Financial institutions process thousands of pages of central bank circulars, regulatory guidelines (RBI / SEC / Basel III), and compliance updates. **BankCompliance AI** is an enterprise-grade, auditable AI copilot built on **Azure Kubernetes Service (AKS)** that delivers sub-second interpretations of RBI Master Directions with exact clause-level legal citations.

---

## 🏛️ 2. Cloud-Native Kubernetes Architecture

```
  [ Branch Officers / Legal Users (bank.mytaxbot.site) ]
                         │
                         ▼
  [ Azure Static Web App (stapp-ht-bankc-p-cin-01) ]
                         │
                         ▼
  [ Azure APIM Gateway (Consumption_0 — Shared Services) ]
    ├── IP Rate Limiting (20 calls/min) & CORS
                         │
                         ▼ (AKS Ingress — Spoke Subnet 10.42.1.0/24)
  ┌─────────────────────────────────────────────────────────────┐
  │         Azure Kubernetes Service (aks-ht-bankc-p-cin-01)    │
  │                                                             │
  │  [ FastAPI Backend Pod ] ──► PII Auto-Masking Engine        │
  │          │ (Auto-redacts PAN, Aadhaar, Account #s)          │
  │          ▼                                                  │
  │  [ Qdrant Vector DB Pod ] ──► 4GB Azure Managed Disk (CSI)  │
  │          │ (Retrieves RBI Master Direction Clauses)         │
  │          ▼                                                  │
  │  [ LiteLLM Proxy Gateway Pod ] (<150MB RAM)                 │
  │          ├── Enforces department token budgets              │
  │          ├── In-memory KV Prompt Caching (<20ms repeat)     │
  │          └── Routes to Azure OpenAI (gpt-5.4-nano in EastUS)│
  │                                                             │
  │  [ KEDA Autoscaler ] ──► Scale-to-Zero (0 replicas idle)    │
  │  [ Azure Policy / OPA ] ──► Enforces non-root container rule │
  └─────────────────────────────────────────────────────────────┘
```

---

## 🔑 3. Key Architectural Decisions & Rationale

| Dimension | Architectural Choice | Enterprise Rationale |
| :--- | :--- | :--- |
| **Compute Engine** | **AKS Free Tier (`Standard_B4ms`)** | Multi-cloud portability (RBI exit strategy), self-hosted stateful Qdrant DB, and Zero-Trust pod isolation. |
| **Vector Storage** | **4GB Managed Disk (`managed-csi`)** | Uses Azure's minimum hardware tier (`E1` Standard SSD, **~$0.15/mo**). Guarantees RBI embeddings persist across `az aks stop` / `az aks start` cycles. |
| **AI Gateway** | **LiteLLM Proxy on AKS** | Sub-second response SLA (<800ms) with Azure OpenAI `gpt-5.4-nano`. Eliminates CPU burst credit exhaustion and local model hosting overhead. |
| **Autoscaling** | **KEDA Event-Driven Scaler** | **Scale-to-Zero (`minReplicaCount: 0`)** when no queries are in queue, eliminating idle RAM/CPU waste. |
| **Security Guardrails** | **Azure Policy for AKS (OPA)** | Enforces banking container security rules (blocks privileged containers, requires memory/CPU limits). |
| **Data Privacy** | **DPDP PII Redaction Engine** | Regex & NER masks Indian PAN cards (`[PAN-REDACTED]`), Aadhaar, and account numbers prior to LLM processing. |

---

## 💰 4. Cost & FinOps Matrix

| Component | Selected Configuration | Idle Cost (Cluster Stopped) | Active Daily Cost |
| :--- | :--- | :---: | :---: |
| **AKS Control Plane** | `sku_tier = "Free"` | **$0.00** | **$0.00** |
| **Compute Node Pool** | 1x `Standard_B4ms` (Ephemeral OS Disk) | **$0.00** | **~$0.30 / day** (~₹25/day) |
| **Qdrant Storage** | 4GB Azure Managed Disk (`managed-csi`) | **~$0.15 / month** | **~$0.15 / month** (₹12/mo) |
| **AI Content Safety** | `F0` Free Tier (5,000 calls/mo) | **$0.00** | **$0.00** |
| **Static Web App** | `Free` Tier (`bank.mytaxbot.site`) | **$0.00** | **$0.00** |
| **TOTAL** | | **~$0.15 / month** | **~$0.15/mo + ₹25/day active** |
