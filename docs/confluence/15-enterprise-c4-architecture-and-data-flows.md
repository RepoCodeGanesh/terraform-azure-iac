# 15. Enterprise C4 Architecture & End-to-End Data Flows

## 1. Metadata & Governance
* **Document ID:** SPEC-ARCH-015
* **Architecture Tier:** Enterprise Architecture & System Design
* **Standard:** C4 Model (Context, Container, Component, Code) + arc42
* **Author / Tech Lead:** Enterprise Platform Engineering Team
* **Source Path:** `docs/confluence/15-enterprise-c4-architecture-and-data-flows.md`
* **Status:** Approved / Production-Hardened

---

## 2. Executive Overview
This specification defines the complete end-to-end software and infrastructure architecture of the **HappyTechies Cloud & AI Platform** using the **C4 Architectural Model**. 

It formalizes the boundaries, containers, internal microagent components, and cryptographic data flows governing **Workload 1 (TaxBot India)** and **Workload 2 (BankCompliance AI)** across the multi-subscription Azure Landing Zone.

---

## 3. C4 Level 1: System Context Diagram

The System Context diagram illustrates the high-level actors, the HappyTechies Cloud & AI Platform boundary, and external systems:

```
+-------------------+       +----------------------------+       +-----------------------------+
|    Tax Filers     |       |  Bank Compliance Officers  |       |     Platform Engineers      |
|  (General Public) |       |   (Risk & Legal Auditors)  |       |   (DevOps & Cloud Admins)   |
+---------+---------+       +--------------+-------------+       +--------------+--------------+
          |                                |                                    |
          | HTTPS                          | HTTPS                              | Git / OIDC
          v                                v                                    v
+----------------------------------------------------------------------------------------------+
|                         HAPPYTECHIES CLOUD & AI ENTERPRISE PLATFORM                          |
|                                                                                              |
|  [Workload 1: TaxBot India]                    [Workload 2: BankCompliance AI]               |
|  Domain: www.mytaxbot.site                     Domain: bank.mytaxbot.site                    |
|  - Serverless Python PaaS                      - Cloud-Native Kubernetes (AKS)               |
|  - Income Tax & Deduction Advisory             - Multi-Agent RBI Compliance Copilot          |
|  - DPDP Act PII Sanitization                   - Sovereign In-Cluster SLM (Qwen 2.5)         |
+-------------------+------------------------------------------+-------------------------------+
                    |                                          |
                    | External API                             | Ingestion / Failover
                    v                                          v
+------------------------------------+       +-------------------------------------------------+
|      External AI Model APIs        |       |          External Regulatory Sources            |
| - Google Gemini 2.0 Flash          |       | - Reserve Bank of India (RBI Circulars)         |
| - Azure OpenAI (gpt-5.4-nano)      |       | - Income Tax Department of India                |
| - Groq LPU (Llama 3.3 70B)         |       | - Central Board of Direct Taxes (CBDT)          |
+------------------------------------+       +-------------------------------------------------+
```

---

## 4. C4 Level 2: Container Diagram (Multi-Subscription Landing Zone)

The Container diagram shows the runtime execution environments, services, and network perimeters:

```
+-------------------------------------------------------------------------------------------------------+
| SUBSCRIPTION: Hub-Prod (3eb8cc01)                                                                     |
|                                                                                                       |
|  +-------------------------------------+      +----------------------------------------------------+  |
|  |  Azure Firewall & Bastion Host      |      |  Private DNS Zones                                 |  |
|  |  (Central Perimeter Security)       |      |  privatelink.vaultcore.azure.net                   |  |
|  +-------------------------------------+      +----------------------------------------------------+  |
+---------------------------------------------------+---------------------------------------------------+
                                                    | VNet Peering
                                                    v
+-------------------------------------------------------------------------------------------------------+
| SUBSCRIPTION: Apps-Prod (f4ffefe1)                                                                    |
|                                                                                                       |
|  [Frontend Presentation Layer]                                                                        |
|  - Azure Static Web App: stapp-ht-bankc-p-cin-01 (React Vite SPA at bank.mytaxbot.site)               |
|                                                                                                       |
|  [Kubernetes Compute Layer: aks-ht-bankc-p-cin-01]                                                    |
|  +-------------------------------------------------------------------------------------------------+  |
|  | Namespace: bank-compliance                                                                      |  |
|  |                                                                                                 |  |
|  |  +----------------------------+   +----------------------------+   +-------------------------+  |  |
|  |  |  bankc-backend (FastAPI)   |-->|  litellm-proxy (Gateway)   |-->|  private-slm-inference  |  |  |
|  |  |  - 4-Agent RAG Orchestrator|   |  - Least-busy Loadbalancer |   |  - Qwen 2.5 0.5B (Ollama|  |  |
|  |  |  - Vector Centroid Guard   |   |  - Gemini ➔ OpenAI Failover|   |  - Zero Cloud Egress    |  |  |
|  |  +--------------+-------------+   +----------------------------+   +-------------------------+  |  |
|  |                 |                                                                               |  |
|  |                 v (Port 6333)                                                                   |  |
|  |  +-------------------------------------------------------------------------------------------+  |  |
|  |  |  qdrant (StatefulSet)                                                                     |  |  |
|  |  |  - 4GB Managed CSI Persistent Disk (StorageClass: managed-csi)                            |  |  |
|  |  |  - Regulatory HNSW Vector Indices (12+ RBI Master Directions)                             |  |  |
|  |  +-------------------------------------------------------------------------------------------+  |  |
|  +-------------------------------------------------------------------------------------------------+  |
+---------------------------------------------------+---------------------------------------------------+
                                                    | Diagnostic Logs & Metrics
                                                    v
+-------------------------------------------------------------------------------------------------------+
| SUBSCRIPTION: Shared-Services (859a785c)                                                              |
|                                                                                                       |
|  +-------------------------------+    +--------------------------------+    +-----------------------+ |
|  |  Central Log Analytics (LAW)  |    |  Azure Monitor Workbook        |    |  Shared Key Vault     | |
|  |  law-ht-ss-p-cin-01           |    |  2d689b14-8f92-4f3a...         |    |  kv-ht-ss-p-cin-01    | |
|  |  - 5 GB/mo Free Data Tier     |    |  - Real-time KQL Dashboards    |    |  - Confluence Secrets | |
|  +-------------------------------+    +--------------------------------+    +-----------------------+ |
+-------------------------------------------------------------------------------------------------------+
```

---

## 5. C4 Level 3: Component Diagram (FastAPI Backend Architecture)

Inside the `bankc-backend` pod, requests flow through a deterministic multi-agent state graph:

```
                                  [ Incoming User Query ]
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │   1. DomainCentroidGuardrail (<3ms)     │
                        │   - Mathematical Vector Sieve           │
                        │   - Intercepts Off-Topic Prompts        │
                        └────────────────────┬────────────────────┘
                                             │ (Valid Banking Query)
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │   2. Governed Semantic Vector Cache     │
                        │   - Cosine Similarity > 0.94            │
                        │   - Model-Scoped (Sovereign vs Cloud)   │
                        └────────────┬────────────────────────────┘
                         (Cache Hit) │              │ (Cache Miss)
                                     │              ▼
                                     │  ┌─────────────────────────────────────────┐
                                     │  │   3. Supervisor Agent (Router)          │
                                     │  │   - DPDP Act PII Masker (PAN/Aadhaar)   │
                                     │  │   - Engine Router (Sovereign vs Cloud)  │
                                     │  └───────────────────┬─────────────────────┘
                                     │                      │
                                     │                      ▼
                                     │  ┌─────────────────────────────────────────┐
                                     │  │   4. Retriever Agent                    │
                                     │  │   - Qdrant Vector Lake Search (k=5)     │
                                     │  │   - SHA-256 Provenance Clause Extractor │
                                     │  └───────────────────┬─────────────────────┘
                                     │                      │
                                     │                      ▼
                                     │  ┌─────────────────────────────────────────┐
                                     │  │   5. Statutory Auditor Agent            │
                                     │  │   - Ground-Truth Reflection Critic      │
                                     │  │   - Citation Integrity Validator        │
                                     │  └───────────────────┬─────────────────────┘
                                     │                      │
                                     │                      ▼
                                     │  ┌─────────────────────────────────────────┐
                                     │  │   6. Synthesizer Agent                  │
                                     │  │   - Cloud: Gemini 2.0 ➔ Azure OpenAI    │
                                     │  │   - Sovereign: In-Cluster Qwen 2.5 SLM  │
                                     │  └───────────────────┬─────────────────────┘
                                     │                      │
                                     └──────────────────────┼─────────────────────┐
                                                            │                     │
                                                            ▼                     ▼
                                            [ Synthesized Audit Memo ]   [ Exec Trace ]
```

---

## 6. End-to-End Sequence Data Flows

### Flow 1: Sovereign In-Cluster SLM Audit (Zero-Egress Mode)
1. **User Request:** User submits a statutory compliance question with target engine `Sovereign SLM`.
2. **In-Memory Guardrail:** `DomainCentroidGuardrail` computes cosine distance against regulatory centroids in <3ms.
3. **Local Vector Search:** `RetrieverAgent` queries local `qdrant:6333` cluster service, retrieving relevant clauses.
4. **Deterministic Auditor:** Auditor confirms clause presence without making any external API calls.
5. **Local SLM Generation:** `SynthesizerAgent` calls `http://private-slm-inference:11434` (Ollama running Qwen 2.5 0.5B).
6. **Zero Egress Verification:** Zero bytes leave the AKS VNet. Response includes cryptographic SHA-256 citations.

### Flow 2: Multi-Cloud Fleet Dynamic Failover
1. **Client Submission:** Query submitted to `bankc-backend`.
2. **LiteLLM Gateway:** Backend routes prompt to `litellm-proxy:4000`.
3. **Primary Route:** LiteLLM attempts call to **Google Gemini 2.0 Flash**.
4. **Automated Failover Trigger:** If Gemini returns HTTP 429 (Rate Limit) or HTTP 503:
   * LiteLLM catches error in <150ms.
   * Seamlessly re-routes payload to **Azure OpenAI `gpt-5.4-nano`**.
5. **Response Delivery:** User receives valid response with telemetry header showing `gemini-2.0-flash (fallback: gpt-5.4-nano)`.

### Flow 3: DPDP Act PII Sanitization Flow
1. **Payload Inspection:** Raw prompt parsed by `dpdp_sanitizer.py`.
2. **Regex Sieve:** Detects 10-digit Indian Permanent Account Numbers (PAN), 12-digit Aadhaar numbers, and 16-digit credit cards.
3. **Redaction:** Replaces sensitive tokens with cryptographic placeholders:
   * `ABCDE1234F` ➔ `[REDACTED_PAN_HASH:e3b0c442]`
4. **Audit Log:** Redaction event logged to `law-ht-ss-p-cin-01` without persisting raw PII data.
