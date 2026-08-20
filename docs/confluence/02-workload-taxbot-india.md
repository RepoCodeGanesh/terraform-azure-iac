# 🤖 Workload 1: TaxBot India (AI Income Tax Advisor)

* **Space:** `HappyTechies Cloud & AI Platform` $\rightarrow$ `Workloads`
* **Live Domain:** [https://www.mytaxbot.site](https://www.mytaxbot.site)
* **Workload Code:** `taxb` (Resource Group: `rg-ht-taxb-p-cin-01`)
* **Status:** `PRODUCTION / LIVE`

---

## 🎯 1. Executive Overview

**TaxBot India** is a conversational AI tax advisor engineered for Indian salaried employees, NRIs, and freelancers navigating the **FY 2026-27 (AY 2027-28)** Income Tax rules. It evaluates tax liabilities under the **Old vs. New Tax Regimes**, computes statutory deductions (80C, 80D, 80CCD(1B), HRA, Home Loan 24(b)), and performs grounded legal statutory retrieval.

---

## 🏗️ 2. Serverless PaaS Architectural Topology

```
 [ Taxpayer / React Web SPA (www.mytaxbot.site) ]
                      │
                      ▼ (HTTPS / Custom Domain DNS)
 [ Azure Static Web App (stapp-ht-taxb-p-cin-01) ]
                      │
                      ▼
 [ Azure APIM Gateway (Consumption_0 — Shared Services) ]
   ├── Rate Limiting: 20 calls/min per IP
   └── CORS & WAF Protection
                      │
                      ▼
 [ Python Linux Function App (func-ht-taxb-p-cin-01) ]
   ├── OpenTelemetry Distributed Tracing ──► law-ht-ss-p-cin-01
   ├── System-Assigned Managed Identity Auth
   ├── Azure AI Content Safety (F0) ──► Jailbreak Defense
   ├── Azure AI Search (srch-ht-taxb-p-cin-01) ──► Statutory RAG
   ├── Cosmos DB (cosmos-ht-taxb-p-cin-01) ──► Session Chat History
   └── Azure OpenAI (gpt-5.4-nano in East US) ──► Tax Computations
```

---

## 📦 3. Component & SKU Specifications

| Service Component | Resource Name | SKU / Tier | Primary Role |
| :--- | :--- | :--- | :--- |
| **Static Web App** | `stapp-ht-taxb-p-cin-01` | `Free` Tier | Hosts React SPA on `www.mytaxbot.site` with free auto-renewing SSL |
| **API Management** | `apim-ht-ss-p-cin-01` | `Consumption_0` | Edge IP rate-limiting (20 calls/min) & CORS protection |
| **Function App** | `func-ht-taxb-p-cin-01` | `Consumption Y1` / `F1` | Python 3.11 backend runtime & calculation engine |
| **Azure OpenAI** | `oai-ht-taxb-p-eus-01` | `S0` Pay-As-You-Go | `gpt-5.4-nano` (2026-03-17) low-latency tax reasoning |
| **Azure AI Search** | `srch-ht-taxb-p-cin-01` | `Basic` / `Free` | Vector search over statutory tax provisions |
| **Cosmos DB** | `cosmos-ht-taxb-p-cin-01` | `Serverless` / `400 RU/s` | Multi-turn chat conversation session persistence |
| **AI Content Safety**| `cs-ht-taxb-p-sea-01` | `F0` Free (5,000 calls/mo) | Prompt injection shield & PII sanitization |

---

## 💰 4. Cost & FinOps Profile

* **Running Idle Cost:** **~$0.10 / month** (from 1 active OpenAI metric alert `alert-openai-throttled-429`).
* **Compute / Database Idle:** **$0.00** (Serverless Consumption Functions & Cosmos DB Free Tier).
* **Storage & LAW Ingestion:** **$0.00** (within the 5GB/month Log Analytics free tier).
