# 04. FinOps & Near-Zero Idle Cost Strategy

* **Space:** `HappyTechies Cloud & AI Platform` -> `FinOps & Governance`
* **Target Audience:** FinOps Leads, Cloud Architects, Engineering Managers
* **Status:** `ACTIVE`

---

## 1. FinOps Philosophy

Enterprise cloud environments often suffer from budget bloat due to idle VM compute, oversized managed databases, and unoptimized storage tiers. The **HappyTechies AI Landing Zone** enforces a **strict near-zero idle cost architecture**:

> **Platform Goal:** Run a full-scale, production-ready, multi-subscription Azure AI Landing Zone with private networking, OIDC identity federation, and Kubernetes workloads for **less than $0.50 / month when idle**, scaling to pennies on-demand.

---

## 2. Master Cost Matrix (Idle vs. Active)

| Cloud Resource | Role in Architecture | Chosen Tier / SKU | Idle Monthly Cost | Active Daily Cost |
| :--- | :--- | :--- | :---: | :---: |
| **AKS Control Plane** | Kubernetes Management | `sku_tier = "Free"` | **$0.00** | **$0.00** |
| **AKS Node Compute** | BankCompliance Container Host | 1x `Standard_B4ms` | **$0.00** (via auto-stop) | **~$0.30 / day** (INR 25/day) |
| **AKS Node Storage** | Node OS Disk | `os_disk_type = "Ephemeral"` | **$0.00** (100% Free) | **$0.00** |
| **Qdrant Storage** | Vector Index Persistence | 4GB Managed Disk (`managed-csi`) | **~$0.15 / month** | **~$0.15 / month** (INR 12/mo) |
| **API Management** | AI Gateway & Rate Limiting | `Consumption_0` | **$0.00** | Pennies / million calls |
| **Function App** | TaxBot Backend Runtime | `Consumption Y1` | **$0.00** | Pennies / million calls |
| **Cosmos DB** | Session Chat History | `Serverless` / Free Tier | **$0.00** | **$0.00** |
| **AI Content Safety** | Jailbreak Shield & PII | `F0` (5,000 calls/mo Free) | **$0.00** | **$0.00** |
| **Log Analytics** | Central LAW & App Insights | `PerGB2018` (5GB/mo Free) | **$0.00** | **$0.00** |
| **Static Web Apps** | `www` & `bank.mytaxbot.site` | `Free` Tier | **$0.00** | **$0.00** |
| **Azure Monitor Alerts** | OpenAI Quota Guardian | 1x Static Metric Alert | **~$0.10 / month** | **~$0.10 / month** |
| **TOTAL** | | | **~$0.25 / month** | **~$0.25/mo + INR 25/day active** |

---

## 3. Five Pillars of FinOps Implementation

### 1. Automated Cluster Lifecycle Governance (`finops-scheduler.yml`)
* GitHub Actions cron workflow automatically calls `az aks stop` every weekday evening at 7:30 PM IST.
* Stops node VM billing completely while preserving the cluster configuration and network state at **$0.00 compute cost**.
* One-click startup via `workflow_dispatch` when development or testing begins.

### 2. KEDA Event-Driven Scale-to-Zero (`minReplicaCount: 0`)
* When no compliance queries are in flight, worker pods scale down to **0 replicas**.
* Zero idle CPU and RAM are allocated, leaving resources available for system processes and Qdrant.

### 3. Ephemeral OS Disks
* Configured `os_disk_type = "Ephemeral"` on the `Standard_B4ms` node pool.
* Leverages the node's local temporary NVMe/SSD cache, completely eliminating the $2-$4/month fee for attached Azure Managed OS Disks.

### 4. LiteLLM Prompt KV Caching & Token Budgeting
* Identical or repeat regulatory questions are served from in-memory cache in **<20ms** at **$0.00 OpenAI API cost**.
* Department token budgets cap usage per team, preventing accidental runaway API expenses.

### 5. Metric Alert Consolidation
* High-cost log query alerts ($1.50/mo each) were avoided in favor of 1 primary static metric alert for OpenAI throttling (`alert-openai-throttled-429` = $0.10/mo).
* Secondary alerts are kept disabled (`enabled = false`) until production scaling is required.
