# BankCompliance AI — Architecture & Request Lifecycle

## 🏛️ System Architecture Topology

```text
[ Compliance Officer / Legal Auditor ]
                  │
                  ▼ (HTTPS / TLS 1.3: bank.mytaxbot.site)
+─────────────────────────────────────────────────────────────+
| Azure Static Web Apps (stapp-ht-bankc-p-cin-01, Free Tier)  |
| • Left Pane: Multi-Agent Interactive Chat & PII Shield      |
| • Right Pane: Split-Screen Regulatory PDF Viewer            |
| • Citation Chips: Auto-jump to exact circular clause & page |
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼ HTTPS POST /api/v1/compliance/query
+─────────────────────────────────────────────────────────────+
| Azure APIM Gateway (apim-ht-ss-p-cin-01, Consumption_0)     |
| • URL Rewrite: /bankc/api/v1/* -> /api/v1/*                 |
| • IP Rate Limiting: 60 requests/min per client IP           |
| • Zero-Cost SSL Termination & CORS Origin Validation        |
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼ Forwarded HTTP (Internal LB)
+─────────────────────────────────────────────────────────────+
| Azure Kubernetes Service (aks-ht-bankc-p-cin-01)            |
| Namespace: bank-compliance (Zero-Trust ClusterIP Isolation) |
|                                                             |
| 1. FastAPI Backend (bankc-backend:8000)                     |
|    ├── DPDP Act PII Sanitizer (Masks PAN, Aadhaar, Acc #)   |
|    ├── Vector Centroid Domain Guardrail (<3ms Cosine Filter)|
|    ├── Governed Semantic Cache (Qdrant Cosine >= 0.90)      |
|    └── 4-Microagent State Graph Orchestrator:               |
|        ├── SupervisorAgent: Intent & Task Decomposition     |
|        ├── RetrieverAgent: Tool-caller on Qdrant HNSW       |
|        ├── AuditorAgent: Reflection & Statutory Verification|
|        └── SynthesizerAgent: Streamed Answer with Citations |
|                                                             |
| 2. Self-Hosted Qdrant Vector DB (Port 6333)                 |
|    └── 4GB Azure Managed Disk (managed-csi, E1 Tier)        |
|                                                             |
| 3. Sovereign In-Cluster SLM Tier (Port 11434)               |
|    └── Quantized Qwen-2.5-0.5B / Phi-3.5-mini for 0-Egress  |
+──────────────────────────────┬──────────────────────────────+
                               │
                               ▼ LiteLLM AI Gateway (Port 4000)
+─────────────────────────────────────────────────────────────+
| Multi-Model AI Router & Resilient Failover                  |
| ├── Primary Engine: Google Gemini 2.0 Flash (Free $0)       |
| └── Standby Failover: Azure OpenAI gpt-5.4-nano (East US)   |
+─────────────────────────────────────────────────────────────+
```

---

## ⚡ End-to-End Query Lifecycle

1. **User Prompt Ingestion:** User submits query via React SPA on `https://bank.mytaxbot.site`.
2. **Edge Security & Routing:** Request passes through Azure APIM (`apim-ht-ss-p-cin-01`) for CORS validation, URL rewriting, and rate-limiting.
3. **PII Sanitization:** FastAPI backend runs regex/NER sanitization to mask Indian PAN cards (`[PAN-REDACTED]`), Aadhaar, and account numbers.
4. **Centroid Domain Sieve:** Evaluates cosine similarity against regulatory centroids ($<3\text{ms}$); immediately rejects non-banking queries.
5. **Governed Semantic Cache:** Checks Qdrant for semantic similarity ($\ge 0.90$). Cache hits return verified answers in $<10\text{ms}$ at $\$0.00$ spend.
6. **Multi-Agent Orchestration:**
   - **Supervisor:** Decomposes complex legal queries into targeted regulatory sub-queries.
   - **Retriever:** Queries Qdrant HNSW index over 14+ RBI Master Directions.
   - **Auditor:** Evaluates retrieved chunks for relevance, statutory freshness, and hallucination risks.
   - **Synthesizer:** Formulates auditable statutory interpretation citing circular numbers, sections, and page numbers via Gemini 2.0 Flash (or fails over to Azure OpenAI `gpt-5.4-nano`).
7. **Client Presentation:** Response streams back to UI; user can click citation chips to open the original PDF to the exact highlighted clause.