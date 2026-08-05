# DevOnboard AI — Application Deployment Plan

**Version**: 1.0  
**Status**: 🟡 Planning Phase — Ready for Development  
**Workload Code**: `dvob`  
**Deployment Target**: `Apps-prod` (Subscription: `f4ffefe1-d689-4059-969c-ccc73e2a11d4`)

---

## 🎯 Application Purpose & Problem Statement

**DevOnboard AI** is an enterprise-grade, AI-powered onboarding and knowledge assistant for technical teams.

### The Problem It Solves
Engineering teams face 3 critical onboarding and knowledge management challenges:

1. **Slow Time-to-First-Commit**: New engineers take 3–4 weeks to understand repository architecture, subscription setup, naming conventions, and deployment standards.
2. **Senior Engineer Interruptions**: Senior cloud engineers waste 15–20 hours per new hire answering repetitive questions about infrastructure and tooling.
3. **Scattered, Outdated Documentation**: Wikis and SharePoint pages become quickly outdated, leaving engineers confused about the current state of the system.

### The Solution
DevOnboard AI delivers **instant, streaming AI answers** grounded in the repository's authoritative documentation (`AGENTS.md`, `README.md`, `architecture.md`, `ROADMAP.md`) via an interactive chat web interface.

---

## 🏗️ Architecture Overview

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │  FRONTEND: Azure Static Web Apps (Free Tier)                        │
 │  • ChatGPT-style Web UI with streaming real-time responses          │
 │  • Hosted at: https://dvob-devonboard-ai.azurestaticapps.net        │
 └───────────────────────────┬─────────────────────────────────────────┘
                             │ HTTPS POST /api/chat
                             ▼
 ┌─────────────────────────────────────────────────────────────────────┐
 │  AI GATEWAY: APIM (apim-ht-ss-p-cin-01) — platform/shared-services  │
 │  • Prompt caching: 0 tokens spent on repeated questions             │
 │  • Token rate limiting: 1,000 tokens/min per user                   │
 │  • Usage telemetry streamed to Log Analytics                        │
 └───────────────────────────┬─────────────────────────────────────────┘
                             │ Chunked SSE Stream (Transfer-Encoding: chunked)
                             ▼
 ┌─────────────────────────────────────────────────────────────────────┐
 │  BACKEND: Python Function App (func-ht-dvob-p-cin-01)               │
 │  • workloads/ai-assistant (deployed via app-prod service connection) │
 │  • Python 3.11 Azure Functions v2 model                             │
 │  • System-Assigned Managed Identity (Keyless Azure OpenAI access)   │
 └─────────────────┬───────────────────────────┬────────────────────────┘
                   │                           │
                   ▼                           ▼
 ┌────────────────────────────┐  ┌─────────────────────────────────────┐
 │ Azure AI Search (Free F1)  │  │ Azure OpenAI (oai-ht-dvob-p-sin-01) │
 │ • Indexes AGENTS.md        │  │ • Model: gpt-4o-mini                │
 │ • Indexes README.md        │  │ • TPM Cap: 10,000 tokens/min        │
 │ • Indexes architecture.md  │  │ • max_tokens per response: 250      │
 │ • Indexes ROADMAP.md       │  │ • Cost: ~$0.000135 per question     │
 └────────────────────────────┘  └─────────────────────────────────────┘
```

---

## 🧩 Infrastructure Mapping (Terraform Workload)

All infrastructure is provisioned inside `workloads/ai-assistant/main.tf` using the workload code `dvob`:

| Resource | Terraform Module / Resource | Azure Resource Name | Subscription |
| :--- | :--- | :--- | :--- |
| **Resource Group** | `azurerm_resource_group.ai_assistant` | `rg-ht-dvob-p-cin-01` | `Apps-prod` |
| **Spoke VNet** | `module.aiast_vnet` | `vnet-ht-dvob-p-cin-01` | `Apps-prod` |
| **VNet Peering** | `module.aiast_to_hub_peering` | Hub ↔ Spoke (bi-directional) | `Hub-prod` ↔ `Apps-prod` |
| **Azure OpenAI** | `module.openai` | `oai-ht-dvob-p-sin-01` | `Apps-prod` |
| **Function App Plan** | `module.aiast_service_plan` | `asp-ht-dvob-p-cin-01` | `Apps-prod` |
| **Function App** | `module.function_app` | `func-ht-dvob-p-cin-01` | `Apps-prod` |
| **Storage Account** | `azurerm_storage_account` (inside function_app) | `sthtdvobpcin01` | `Apps-prod` |
| **App Insights** | `azurerm_application_insights` (inside function_app) | `appi-ht-dvob-p-cin-01` | `Apps-prod` |
| **RBAC Role** | `azurerm_role_assignment.func_openai_user` | `Cognitive Services OpenAI User` | `Apps-prod` |
| **APIM Backend** | `azurerm_api_management_backend.openai_backend` | `openai-backend-dvob` | `Shared-services` |

---

## 🔗 Shared Services Cross-References (`platform/shared-services`)

The DevOnboard AI workload **reads** (does not own) these shared resources. The Function App plan is now workload-owned in `Apps-prod`, not shared-services.

| Shared Resource | Azure Name | Purpose |
| :--- | :--- | :--- |
| **Log Analytics Workspace** | `law-ht-ss-p-cin-01` | Application Insights telemetry & token usage metrics |
| **API Management** | `apim-ht-ss-p-cin-01` | Prompt caching, rate limiting & AI gateway |

---

## 🔐 Security Architecture (Zero-Trust / Keyless)

| Security Control | Implementation |
| :--- | :--- |
| **Authentication to Azure OpenAI** | System-Assigned Managed Identity + `DefaultAzureCredential()` (no API keys) |
| **RBAC Role Grant** | `Cognitive Services OpenAI User` granted to Function App identity on OpenAI scope |
| **State File Auth** | `use_azuread_auth = true` in `backend.hcl` (no storage keys) |
| **Pipeline Auth** | Workload Identity Federation (OIDC) via `app-prod` service connection |

---

## 💰 Cost Strategy (Near-$0 Running Cost)

| Component | SKU | Idle Cost | Active Cost |
| :--- | :--- | :--- | :--- |
| **Azure Static Web Apps** | Free Tier | $0.00/month | $0.00/month |
| **Azure Function App** | Consumption Y1 | $0.00/month | ~$0.00 (1M free requests) |
| **API Management** | `Consumption_0` | $0.00/month | ~$0.00 (1M free calls) |
| **Azure OpenAI `gpt-4o-mini`** | Pay-As-You-Go | $0.00/month | ~$0.000135/question |
| **Azure AI Search** | Free F1 | $0.00/month | $0.00/month |
| **Log Analytics** | PerGB2018 | ~$0.01/month | Pay-per-GB |

**Estimated Total Monthly Cost**: **$0.01 – $1.35** depending on usage volume.

---

## 🤖 Token Optimization Strategy

To keep Azure OpenAI token usage minimal:

1. **APIM Prompt Caching**: Repeat questions cost **0 tokens** — answered from gateway cache.
2. **Top-2 Chunk Retrieval**: AI Search returns only the top 2 most relevant doc snippets (~250 words max input context).
3. **Output Token Cap**: `max_tokens = 250` enforced in all API calls.
4. **TPM Quota Cap**: OpenAI deployment capacity hardcoded to `sku_capacity = 10` (10,000 tokens/min max) — prevents surprise bills.

---

## 🚀 Application Components (To Be Built in Phase 2)

> **NOTE**: Infrastructure Terraform code is DONE. The following application code is planned for the next phase.

### Backend — Python Azure Function App (`func-ht-dvob-p-cin-01`)
- **File**: `workloads/ai-assistant/app/function_app.py`
- **Endpoint**: `POST /api/chat`
- **Key Libraries**: `azure-functions`, `azure-identity`, `openai`
- **Auth**: `DefaultAzureCredential()` → `get_bearer_token_provider()`
- **Streaming**: `stream=True` with Server-Sent Events (SSE / `text/event-stream`)

### Frontend — Azure Static Web Apps Chat UI
- **File**: `workloads/ai-assistant/frontend/index.html`
- **Tech**: HTML5 + Vanilla JavaScript (no framework needed)
- **Features**:
  - Real-time streaming message display (tokens appear word-by-word)
  - Markdown rendering for code blocks
  - Dark mode chat interface
  - "Clear Chat" button to reset conversation

---

## 📋 Deployment Checklist (When Ready)

### Infrastructure (Already Coded — `workloads/ai-assistant/main.tf`)
- [x] Resource Group (`rg-ht-dvob-p-cin-01`)
- [x] Spoke VNet (`vnet-ht-dvob-p-cin-01`, `10.40.0.0/16`)
- [x] VNet Peering to Hub (`vnet-ht-hub-p-cin-01`)
- [x] Azure OpenAI Account (`oai-ht-dvob-p-sin-01`, `gpt-4o-mini`)
- [x] Workload-local Function App plan (`asp-ht-dvob-p-cin-01`, Consumption Y1)
- [x] Python Function App (`func-ht-dvob-p-cin-01`, Python 3.11)
- [x] System-Assigned Managed Identity + RBAC role assignment
- [x] APIM Backend Registration (`openai-backend-dvob`)

### Application Code (Planned — Next Phase)
- [ ] Python Backend: `function_app.py` with `/api/chat` streaming endpoint
- [ ] `requirements.txt`: `azure-functions`, `azure-identity`, `openai`
- [ ] `host.json`: Azure Functions v4 extension bundle
- [ ] Frontend: `index.html` — Streaming Chat Web UI
- [ ] APIM Policy XML: Prompt caching + token rate-limiting

### CI/CD Pipeline (`pipelines/azure-cicd-ai-assistant.yml`)
- [x] Service Connection: `app-prod` (Workload Identity Federation)
- [x] Working Directory: `workloads/ai-assistant`
- [ ] Add `frontend/` deployment stage to Azure Static Web Apps
- [ ] Add `app/` Function App deployment step (zip deploy)

---

## 📁 Repository Location

This plan is stored at:
```
docs/ai-assistant/DEVONBOARD_AI_PLAN.md
```

The infrastructure Terraform code lives at:
```
workloads/ai-assistant/
```
