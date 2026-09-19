# 🛠️ Shared Services Layer Plan & Architecture

The **Shared Services** layer provisions common platform tools, security infrastructure, monitoring telemetry, and AI Gateway proxies consumed by all application workloads across the Azure Landing Zone.

---

## 🎯 Shared Components & Cost-Optimized SKUs

| Component | Resource Type | Target SKU / Configuration | Role in Landing Zone |
| :--- | :--- | :--- | :--- |
| **API Management** | `apim` | `Consumption_0` ($0 idle) | AI Gateway proxy (OpenAI rate-limiting, prompt caching, token logging). |
| **Log Analytics** | `law` | `PerGB2018` (30-day retention) | Centralized log ingestion, App Insights telemetry, and audit logs. |
| **Key Vault** | `kv` | `Standard` (RBAC enabled) | Central secret management for API keys and certificates. |
| **Azure OpenAI** | `oai` | `S0` (`gpt-5.4-nano`) | Central AI inference endpoint consumed by TaxBot & BankCompliance. |
| **Azure AI Content Safety** | `cs` | `F0` (5k calls/month free) | Real-time text moderation & jailbreak prompt protection. |
| **Azure AI Doc Intelligence** | `di` | `F0` (500 pages/month free) | Layout & OCR parsing for regulatory circulars and tax forms. |
| **Azure Managed Grafana** | `amg` | `Essential` ($0.00 / 30 users) | Centralized 5-Pillar operational dashboard for platform & workloads. |
| **Central Action Group** | `ag` | Email Alerting | Centralized notifications for FinOps budget thresholds & outages. |
| **Private DNS Zones** | `dns` | Standard | Name resolution for private endpoints across connected VNets. |
| **VNet Peering** | `peer` | Bidirectional | Connects Shared Services VNet directly to the Central Hub VNet. |

---

## 🚀 Deployment Prerequisites

* The `platform/bootstrap` layer must be applied first (provides state storage).
* The `platform/hub` layer must be applied second (provides central Hub VNet target for peering).

---

## ⚙️ How to Deploy

```bash
cd platform/shared-services
terraform init -backend-config=backend.hcl
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```
