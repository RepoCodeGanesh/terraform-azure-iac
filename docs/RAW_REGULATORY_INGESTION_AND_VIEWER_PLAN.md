# Architecture & Execution Plan: Enterprise Auditable Document Intelligence & LLMOps Platform

## 🎯 Executive Overview & Industry Context
* **Industry Sector:** **RegTech (Regulatory Technology / BFSI — Banking, Financial Services & Insurance)**
* **Workload Scope:** **Phase 10: Automated Raw PDF Ingestion, Multi-Model Routing (Gemini + OpenAI), Split-Screen Document Intelligence & CI/CD LLMOps Quality Gates**
* **Target Domain:** Bank Compliance AI Copilot ([https://bank.mytaxbot.site](https://bank.mytaxbot.site))

This platform bridges raw, signed regulatory PDFs issued by the Reserve Bank of India (RBI) with an automated layout-aware parsing pipeline, deep-linked vector embeddings in Qdrant on AKS, a dual-model LLM router (Google Gemini 2.0 Flash + Azure OpenAI), an auditable split-screen React portal, and automated CI/CD hallucination-prevention quality gates.

---

## 🏛️ End-to-End System Architecture

```mermaid
graph TD
    subgraph "1. Raw Data Lake & Ingestion"
        A["Official RBI Master Directions (rbi.org.in)"] -->|Periodic Crawler / Ingestion Script| B["Azure Blob Storage: 'rbi-raw-pdfs'<br/>(Tier 1 Raw Storage)"]
        B -->|Multimodal Layout Parsing| C["Google Gemini 2.0 Flash (Free)<br/>+ Layout-Aware Docling Parser"]
        C -->|Extracts Tables + Exact Page Maps| D["Deep-Linked Regulatory Payload Catalog"]
    end

    subgraph "2. Qdrant Vector Engine on AKS"
        D -->|Vector Upsert Worker| E["Qdrant Vector DB on AKS<br/>(4GB Managed CSI Volume)"]
        E -->|Sub-10ms Vector Retrieval| F["FastAPI Backend (/compliance/query)"]
    end

    subgraph "3. Multi-Model AI Gateway (LiteLLM)"
        F --> G["LiteLLM AI Proxy<br/>(In-Memory Prompt Caching)"]
        G -->|Primary / Heavy PDF Analysis (Free $0)| H["Google Gemini 2.0 Flash<br/>(Google AI Studio Free Tier)"]
        G -->|Low-Latency Private VNet / Failover| I["Azure OpenAI<br/>(gpt-5.4-nano in rg-ht-ss-p-cin-01)"]
    end

    subgraph "4. Interactive Split-View React Portal (bank.mytaxbot.site)"
        H --> J["Left Pane: BankCompliance AI Copilot & PII Shields"]
        F -->|Stream PDF Blob URL & Page Numbers| K["Right Pane: Live Interactive PDF Viewer<br/>(Auto-jumps & highlights exact clause)"]
        J -.->|Click Citation e.g. 'Page 14'| K
    end

    subgraph "5. Automated CI/CD LLMOps Quality Gates"
        L["Git Pull Request (Code / Prompt Change)"] --> M["GitHub Actions Evaluation Suite"]
        M -->|Ragas Benchmark on 100+ Test Cases| N{"RAG Triad Gate"}
        N -->|Faithfulness > 95%<br/>Relevancy > 90%| O["✅ PR Approved & Deployed to AKS"]
        N -->|Hallucination Detected| P["❌ Build Blocked with Audit Report"]
    end
```

---

## 🤖 Multi-Model LLM Routing Strategy: Gemini + OpenAI

### Current Setup vs. Phase 10 Merged Setup

| Architectural Dimension | ⚙️ Current Setup (Phase 9) | 🚀 Phase 10 Merged Setup |
| :--- | :--- | :--- |
| **Primary LLM** | **Azure OpenAI (`gpt-5.4-nano`)** | **Google Gemini 2.0 Flash** *(via Google AI Studio Free Tier)* |
| **Secondary / Failover LLM** | None (Single provider) | **Azure OpenAI (`gpt-5.4-nano`)** *(Instant sub-200ms failover)* |
| **Document Ingestion Engine** | Python regex chunker on `.md` files | **Gemini 2.0 Flash Multimodal** (Reads 150-page raw PDFs & tables natively) |
| **Daily LLM Token Cost** | Pay per token consumed | **$0.00 / month** *(Uses 1,500 requests/day Free Tier in Google AI Studio)* |
| **Context Window** | 128,000 tokens | **1,000,000 tokens** (Zero document truncation) |

### LiteLLM Dual-Model Configuration (`app/bank-compliance/k8s/litellm/config.yaml`):

```yaml
model_list:
  # 🥇 PRIMARY LLM: Google Gemini 2.0 Flash (Fast & 100% Free)
  - model_name: compliance-copilot
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: "os.environ/GEMINI_API_KEY"

  # 🥈 SECONDARY / FAILOVER LLM: Azure OpenAI (gpt-5.4-nano in private VNet)
  - model_name: compliance-copilot
    litellm_params:
      model: azure/gpt-5.4-nano
      api_base: "os.environ/AZURE_OPENAI_ENDPOINT"
      api_key: "os.environ/AZURE_API_KEY"
      api_version: "2024-06-01"

router_settings:
  routing_strategy: "latency-based-routing"
  fallbacks: [{"compliance-copilot": ["azure/gpt-5.4-nano"]}]
  num_retries: 3
  timeout: 30
```

---

## 📋 4 Core Engineering Modules

### Module 1: Raw Regulatory Data Lake & AI Ingestion
* **Storage Architecture:** Dedicated Workload Storage Account **`sthtbankcpcin01`** in resource group **`rg-ht-bankc-p-cin-01`** (`Apps-prod` sub) for 100% workload isolation and independent lifecycle. (TaxBot remains unchanged as-is).
* **Blob Container:** **`rbi-raw-pdfs`** with CORS policy configured for `https://bank.mytaxbot.site` to enable zero-latency direct browser PDF streaming.
* **Crawler & Deduplication:** Python ingestion worker with SHA-256 integrity checksums.
* **Layout Parsing:** Gemini 2.0 Flash extracts complex banking tables, circular amendments, and page-level section bounding boxes.

### Module 2: Deep-Linked Qdrant Vector Database
* **Storage:** 4GB Managed CSI Persistent Volume on AKS (`aks-ht-bankc-p-cin-01`).
* **Payload Schema:**
  ```json
  {
    "circular_no": "RBI/2023-24/108",
    "title": "Master Direction on Information Technology Governance",
    "clause_id": "Section 8.1.3",
    "clause_title": "Cloud Security & Data Localization",
    "text": "All regulated entities storing customer financial data in cloud environments must ensure primary data resides in India...",
    "pdf_filename": "rbi_it_governance_2023.pdf",
    "page_start": 14,
    "page_end": 15,
    "pdf_blob_url": "https://sthtssbpcin01.blob.core.windows.net/rbi-raw-pdfs/it-governance-2023.pdf"
  }
  ```

### Module 3: Split-View Compliance Portal (`bank.mytaxbot.site`)
* **Dual-Pane Interface:**
  * **Left Pane (50%):** Multi-turn conversational copilot, DPDP Act PII sanitization alerts, and compliance risk badges (✅ Compliant, ⚠️ High Risk, ❌ Non-Compliant).
  * **Right Pane (50%):** Integrated PDF document viewer (`react-pdf` / PDF.js).
* **Interactive Deep-Link:** Clicking any citation pill (e.g. `[📜 RBI IT Master Direction ➔ Page 14]`) automatically scrolls the live PDF to Page 14 and highlights the corresponding clause in yellow.

### Module 4: Automated CI/CD LLMOps Quality & Safety Gates
* **Integrated into GitHub Actions (`.github/workflows/app-bank-compliance.yml`):**
  * Automated **Ragas / TruLens** benchmarking against 100+ statutory test cases on every Git PR.
  * **Quality Thresholds (Blocks PR on Failure):**
    * **Faithfulness > 95%** (Detects & blocks hallucinations).
    * **Answer Relevancy > 90%** (Ensures answers directly address queries).
    * **Context Precision & Recall > 90%** (Validates Qdrant retrieval quality).
  * **Automated Red-Teaming:** Tests prompt injection and jailbreak resistance before promoting to AKS.

---

## 💰 Cost & FinOps Profile

| Component | Technology / SKU | Monthly Idle Cost | Monthly Active Cost |
| :--- | :--- | :---: | :---: |
| **AKS Cluster VM** | 1x `Standard_B4ms` (4 vCPUs, 16GB RAM) | **$0.00** *(via auto-shutdown)* | ~$13.78 / hr (during tests) |
| **Vector DB Storage** | 4GB Azure Managed CSI Disk (`Standard_LRS`) | ~$0.15 (₹12 / mo) | ~$0.15 (₹12 / mo) |
| **Raw PDF Data Lake** | Azure Blob Storage (`Hot/Cool`) | ~$0.05 (₹4 / mo) | ~$0.05 (₹4 / mo) |
| **Google Gemini 2.0 Flash** | Google AI Studio Free Tier (1,500 req/day) | **$0.00 (₹0)** | **$0.00 (₹0)** |
| **Azure OpenAI (`gpt-5.4-nano`)** | Pay-as-you-go (Token consumed) | **$0.00** | ~$0.20 – $0.50 (₹16 – ₹40) |
| **CI/CD Quality Gates** | GitHub Actions Runner + Gemini Judge | **$0.00 (₹0)** | **$0.00 (₹0)** |
| **Frontend CDN & SSL** | Azure Static Web Apps (Free Tier) | **$0.00 (₹0)** | **$0.00 (₹0)** |
| **Total Monthly Baseline** | | **~$0.20 / mo (~₹16 / mo)** | **~$1.50 – $3.00 / mo (~₹120 – ₹250 / mo)** |
