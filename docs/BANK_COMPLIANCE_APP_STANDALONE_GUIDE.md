# 🏦 Standalone Application Repository Guide: `bank-compliance-ai-app`

> [!NOTE]
> **Monorepo Migration Notice:**
> The `bank-compliance-ai-app` codebase has been integrated directly into this monorepo under [`app/bank-compliance/`](../app/bank-compliance/).
> Please refer to [`app/bank-compliance/README.md`](../app/bank-compliance/README.md) and [`docs/PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) for the active production architecture. This document is retained for historical decoupling and architectural reference.

---

## 🎯 Repository Overview & Decoupling

Following Microsoft Cloud Adoption Framework (CAF) role separation:
* **Infrastructure Repo (`terraform-azure-iac`)**: Deploys the AKS Free Tier cluster, spoke VNet, Content Safety (`F0`), and Managed Identities in `workloads/bank-compliance-ai-aks`.
  * **Local Path:** `c:\Users\RichT\OneDrive\Documents\Repos\terraform-azure-iac`
  * **Remote URL:** `https://github.com/RepoCodeGanesh/terraform-azure-iac`
* **Application Repo (`bank-compliance-ai-app`)**: Contains the frontend SPA, FastAPI backend, Qdrant vector client, LiteLLM gateway configuration, Helm charts, and CI/CD pipelines.
  * **Local Path:** `c:\Users\RichT\OneDrive\Documents\Repos\bank-compliance-ai-app`
  * **Remote URL:** `https://github.com/RepoCodeGanesh/bank-compliance-ai-app`

### 🗂️ Local Workspace Layout (Sibling Repositories)
```
c:\Users\RichT\OneDrive\Documents\Repos\
├── terraform-azure-iac/       # Infrastructure repository (Landing Zone, AKS IaC)
└── bank-compliance-ai-app/    # Application repository (FastAPI, React, Helm, KEDA)
```

---

## 📁 Recommended Repository Layout

```
bank-compliance-ai-app/
├── .github/
│   └── workflows/
│       ├── build-and-deploy.yml    # CI/CD: Docker build ➔ Push ghcr.io ➔ Helm AKS
│       └── finops-scheduler.yml    # Cron: Auto-stop cluster at 8PM / manual dispatch
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py           # /api/v1/compliance/query, /healthz
│   │   │   └── pii_shield.py       # Indian PAN/Aadhaar/Account # regex & NER mask
│   │   ├── core/
│   │   │   ├── config.py           # Settings & Env vars
│   │   │   └── security.py         # Content Safety & Auth
│   │   ├── services/
│   │   │   ├── qdrant_service.py   # Qdrant client & HNSW search
│   │   │   └── rbi_chunker.py      # Clause-aware Master Direction chunker
│   │   └── main.py                 # FastAPI application & OTel instrumentation
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/             # ChatWindow, CitationCard, PIIBanner
│   │   ├── App.jsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── package.json
│   └── staticwebapp.config.json    # Routing, CORS, and fallback for bank.mytaxbot.site
├── k8s/
│   ├── litellm/
│   │   ├── config.yaml             # LiteLLM proxy config (Azure OpenAI routing & quotas)
│   │   └── deployment.yaml         # LiteLLM proxy pod (<150MB RAM)
│   ├── qdrant/
│   │   └── values.yaml             # Helm values: 4GB Managed Disk (managed-csi)
│   └── keda/
│       └── scaledobject.yaml       # Scale-to-Zero (minReplicaCount: 0)
└── README.md
```

---

## ⚙️ Key Component Specifications

### 1. LiteLLM Proxy Gateway (`k8s/litellm/config.yaml`)

```yaml
model_list:
  - model_name: gpt-5.4-nano
    litellm_params:
      model: azure/gpt-5.4-nano
      api_base: https://oai-ht-taxb-p-eus-01.openai.azure.com/
      api_version: "2026-03-17"

general_settings:
  # Enable in-memory KV prompt caching (serves repeat queries in <20ms at $0)
  enable_prompt_caching: true
  cache_type: "in-memory"
  cache_ttl: 7200 # 2 hours

router_settings:
  routing_strategy: "latency-based-routing"
  num_retries: 3
  timeout: 30
```

---

### 2. Qdrant Persistent Storage (`k8s/qdrant/values.yaml`)

```yaml
persistence:
  enabled: true
  storageClassName: "managed-csi"
  size: 4Gi
  accessModes:
    - ReadWriteOnce

resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "1Gi"
```

---

### 3. KEDA Scale-to-Zero Autoscaler (`k8s/keda/scaledobject.yaml`)

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: bankc-backend-scaler
  namespace: bank-compliance
spec:
  scaleTargetRef:
    name: bankc-backend
  minReplicaCount: 0 # True Scale-to-Zero FinOps when idle
  maxReplicaCount: 5
  cooldownPeriod: 300
  triggers:
    - type: cpu
      metadata:
        type: Utilization
        value: "70"
```

---

### 4. Automated FinOps Lifecycle Scheduler (`.github/workflows/finops-scheduler.yml`)

```yaml
name: FinOps Cluster Lifecycle Scheduler

on:
  schedule:
    - cron: '0 14 * * 1-5' # 14:00 UTC = 19:30 IST (Auto-stop every weekday evening)
  workflow_dispatch:
    inputs:
      action:
        description: 'Cluster Action (start or stop)'
        required: true
        default: 'start'
        type: choice
        options:
          - start
          - stop

permissions:
  id-token: write
  contents: read

jobs:
  aks-lifecycle:
    runs-on: ubuntu-latest
    steps:
      - name: Azure OIDC Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.APP_CLIENT_ID }}
          tenant-id: 4cef0d84-84d6-4ed0-8abe-773b015bcf99
          subscription-id: f4ffefe1-d689-4059-969c-ccc73e2a11d4

      - name: Execute Cluster Lifecycle
        run: |
          ACTION="${{ inputs.action || 'stop' }}"
          echo "Executing AKS $ACTION on cluster aks-ht-bankc-p-cin-01..."
          az aks $ACTION --resource-group rg-ht-bankc-p-cin-01 --name aks-ht-bankc-p-cin-01 --no-wait
          echo "Cluster $ACTION command dispatched successfully!"
```

---

## 🌐 Custom Subdomain Setup: `bank.mytaxbot.site`

1. The Static Web App is deployed as `stapp-ht-bankc-p-cin-01`.
2. Add a DNS **CNAME Record** in your domain registrar:
   * **Type:** `CNAME`
   * **Name / Subdomain:** `bank`
   * **Target / Destination:** `<your-static-web-app-url>.azurestaticapps.net`
3. Azure issues a **100% Free Managed SSL Certificate** automatically.
4. Your application will be live at: **`https://bank.mytaxbot.site`**!
