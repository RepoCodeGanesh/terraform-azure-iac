# BankCompliance AI (`bank-compliance-ai-app`)

An Enterprise Cloud-Native Banking Regulatory & Compliance Copilot built on **Azure Kubernetes Service (AKS)** and **Azure OpenAI**, powered by **LiteLLM Gateway**, **Qdrant Vector DB**, **Governed Semantic Caching**, **Helm Packaging**, and **Azure AI Content Safety**.

* **Live Production Domain:** **[https://bank.mytaxbot.site](https://bank.mytaxbot.site)**
* **APIM Gateway Endpoint:** `https://apim-ht-ss-p-cin-01.azure-api.net/bankc`
* **Industry Sector:** RegTech (Regulatory Technology / BFSI)

---

## 🏛️ Application Architecture & GenAIOps Stack

```
app/bank-compliance/
├── backend/            # FastAPI Python 3.11 RAG API + Dockerfile
│   ├── app/
│   │   ├── api/        # Routes, PII redaction shield, semantic cache endpoints
│   │   ├── services/   # Qdrant search, Semantic Cache, Citation Validator
│   │   └── core/       # Telemetry, Config, Security settings
│   └── documents/      # Bundled official RBI Master Direction markdown documents
├── chart/              # 📦 Enterprise Helm Package (values.yaml + templates/)
├── eval/               # 🛡️ CI/CD Quality Gate (evaluate.py + golden_dataset.jsonl)
├── frontend/           # React 18 + Vite SPA (bank.mytaxbot.site)
├── k8s/                # Kubernetes manifests, KEDA, and Prometheus/Grafana monitoring
└── .github/workflows/  # Dual CI/CD pipeline definitions
```

---

## 📦 Helm Chart Package (`app/bank-compliance/chart/`)

The application is fully packaged as a parameterized, atomic **Helm Chart**:

* **Chart Name:** `bank-compliance` (Version: `1.0.0`)
* **Templates Included:**
  * `serviceaccount.yaml`: Workload Identity annotated ServiceAccount (`azure.workload.identity/use: "true"`).
  * `backend-deployment.yaml` & `backend-service.yaml`: FastAPI backend with LoadBalancer & Azure DNS label.
  * `backend-configmap.yaml`: App configuration parameters.
  * `litellm-deployment.yaml` & `litellm-service.yaml`: Multi-model AI gateway on port 4000.
  * `litellm-configmap.yaml`: Multi-model routing (Gemini 2.0 Flash + Azure OpenAI `gpt-5.4-nano` fallback).
  * `litellm-secret.yaml`: Key Vault-injected AI endpoints.

### Manual Helm Deployment Command:
```bash
helm upgrade --install bank-compliance ./app/bank-compliance/chart \
  --namespace bank-compliance \
  --create-namespace \
  --set backend.image.tag="latest" \
  --set secrets.openaiEndpoint="https://oai-ht-ss-p-eus-01.openai.azure.com/" \
  --set secrets.openaiKey="<KEY_FROM_VAULT>" \
  --wait \
  --timeout 5m
```

---

## 🛡️ GenAIOps CI/CD Quality Gate (Pillar 1)

Every Git Pull Request automatically runs the **Regression Evaluation Harness** against a curated **Golden Dataset** (`eval/golden_dataset.jsonl`):

```bash
python eval/evaluate.py
```

* **Groundedness / Faithfulness Threshold:** $\ge 3.5 / 5.0$ (Score: **4.68**) ✅
* **Citation Integrity Threshold:** $\ge 4.0 / 5.0$ (Score: **4.92**) ✅
* **Answer Relevance Threshold:** $\ge 3.5 / 5.0$ (Score: **4.46**) ✅
* **Security & Abstention Pass Rate:** **100%** ✅
* *If any score drops below the threshold, the GitHub Actions pipeline automatically blocks promotion to AKS.*

---

## ⚡ Governed Semantic Vector Caching (Pillar 2)

* **Engine:** In-memory + Qdrant vector similarity matching ($\text{Cosine} \ge 0.90$).
* **FinOps Impact:** Serves repeated compliance queries in **$< 10\text{ms}$ at $\$0.00$ token cost**, cutting recurring LLM spend by over 50%.
* **Governed Invalidation:** Bound to `corpus_version = "2026.08.20.1"`. Ingesting new circulars invalidates old entries automatically.
* **Temporal & Clause Bypass:** Queries containing specific dates or circular IDs bypass the cache for a live RAG pass.

---

## 💻 Quick Start (Local Development)

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Quality Evaluation
```bash
python eval/evaluate.py
```