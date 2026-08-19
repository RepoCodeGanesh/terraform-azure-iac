# 🇮🇳 TaxBot India Workload Infrastructure (`workloads/tax-advisor`)

This directory contains the Terraform infrastructure code for **TaxBot India** — an Enterprise AI Income Tax & Salary Optimization Copilot provisioned on **Azure Serverless PaaS** following Microsoft Cloud Adoption Framework (CAF) patterns.

* **Production Domain:** [https://www.mytaxbot.site](https://www.mytaxbot.site)
* **Target Subscription:** `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`)
* **Spoke Network:** `10.41.0.0/16` (`vnet-ht-taxb-p-cin-01`)
* **Resource Group:** `rg-ht-taxb-p-cin-01` (Central India)

---

## 🎯 Architecture Overview

```
                   ┌─────────────────────────────────────────┐
                   │         Dual CI/CD (GHA & ADO)          │
                   └────────────────────┬────────────────────┘
                                        │ (Workload Identity Federation)
                                        ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                           Azure Subscriptions                             │
  ├───────────────────┬───────────────────┬───────────────────┬───────────────┤
  │     Bootstrap     │     Hub-prod      │  Shared-services  │   Apps-prod   │
  │   7689ad81-...    │   3eb8cc01-...    │   859a785c-...    │  f4ffefe1-... │
  ├───────────────────┼───────────────────┼───────────────────┼───────────────┤
  │ • Remote State    │ • Hub VNet        │ • Log Analytics   │ • Spoke VNet  │
  │   (sthtbootpcin01)│   (10.0.0.0/16)   │   (law-ht-ss...)  │   (10.41.0/16)│
  │                   │                   │ • APIM Gateway    │ • Function App│
  │                   │                   │   (Consumption)   │ • OpenAI API  │
  │                   │                   │ • Shared Key Vault│ • AI Search   │
  │                   │                   │   (kv-ht-ss-p...) │ • Cosmos DB   │
  │                   │                   │                   │ • SWA Frontend│
  └───────────────────┴───────────────────┴───────────────────┴───────────────┘
```

---

## 🔑 Key Resource Specifications

| Resource | Name / Resource Type | Selected SKU / Mode | Idle Running Cost |
| :--- | :--- | :--- | :---: |
| **Frontend UI** | `stapp-ht-taxb-p-cin-01` | Azure Static Web App `Free` | **$0.00 / month** |
| **Backend API** | `func-ht-taxb-p-cin-01` | Linux Function App (`Consumption Y1` Python 3.11) | **$0.00 idle** |
| **Vector DB / RAG** | `srch-ht-taxb-p-cin-01` | Azure AI Search `Free` (1 index, 50MB storage) | **$0.00 / month** |
| **Chat Memory** | `cosmos-ht-taxb-p-cin-01`| Cosmos DB Serverless (`400 RU/s` Free Tier) | **$0.00 / month** |
| **Observability Agent** | `oa-ht-taxb-p-eus-01` | Azure Copilot Observability Agent (`eastus`) | **$0.00 / month** |
| **Networking** | `vnet-ht-taxb-p-cin-01` | Spoke VNet (`10.41.0.0/16`) + VNet Peering | **$0.00 / month** |

---

## 🚀 Automated Deployment Instructions

### 1. Initialize Terraform Backend & Providers
```bash
terraform init -backend-config=backend.hcl
```

### 2. Plan Infrastructure
```bash
terraform plan -var-file=prod.tfvars -out=tfplan
```

### 3. Apply Infrastructure (Zero-Touch Cloudflare DNS + Custom Domain)
```bash
terraform apply tfplan
```

---

## 🌐 Automated Cloudflare DNS & Custom Domain Architecture (`dns_cloudflare.tf`)

Custom domain registration (`www.mytaxbot.site`) and DNS management are **100% automated as code**:

1. **Dynamic Key Vault Authentication**: Cloudflare API Token is retrieved at runtime from `kv-ht-ss-p-cin-01/secrets/cloudflare-api-token`.
2. **Automated CNAME Creation**: Resource `cloudflare_record.taxb_cname` automatically creates `www` ➔ `victorious-tree-xxx.azurestaticapps.net`.
3. **Race Condition Prevention**: Resource `time_sleep.wait_for_dns` introduces an automatic 10-second edge propagation buffer.
4. **Automated Azure SSL Binding**: Resource `azurerm_static_web_app_custom_domain.taxb_custom_domain` binds `www.mytaxbot.site` to Azure Static Web Apps and automatically issues the free SSL certificate in a **single pass**.
