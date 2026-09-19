# 🏦 BankCompliance AI Workload Infrastructure (`workloads/bank-compliance-ai-aks`)

This directory contains the Terraform infrastructure code for **BankCompliance AI** — an Enterprise Cloud-Native Banking Regulatory & Compliance Copilot provisioned on **Azure Kubernetes Service (AKS)** following Microsoft Cloud Adoption Framework (CAF) patterns.

* **Workload Infrastructure:** `workloads/bank-compliance-ai-aks`
* **Application Code:** [`app/bank-compliance`](../../app/bank-compliance/) (React Vite SPA + FastAPI + Helm + Eval Harness)
* **Live Production Domain:** [https://bank.mytaxbot.site](https://bank.mytaxbot.site)
* **APIM Gateway Endpoint:** `https://apim-ht-ss-p-cin-01.azure-api.net/bankc`

---

## 🎯 Architecture Overview

```
                   ┌─────────────────────────────────────────┐
                   │         GitHub Actions CI/CD            │
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
  │   (sthtbootpcin01)│   (10.0.0.0/16)   │   (law-ht-ss...)  │   (10.42.0/16)│
  │                   │                   │ • APIM Gateway    │ • AKS Cluster │
  │                   │                   │   (Consumption)   │ • Content Safe│
  │                   │                   │                   │ • SWA Frontend│
  └───────────────────┴───────────────────┴───────────────────┴───────────────┘
```

---

## 🔑 Key Resource Specifications

| Resource | Name / Resource Type | Selected SKU / Mode | Idle Running Cost |
| :--- | :--- | :--- | :---: |
| **AKS Cluster** | `aks-ht-bankc-p-cin-01` | `sku_tier = "Free"` | **$0.00 / month** |
| **AKS Node Pool** | 1x `Standard_B4ms` (4 vCPU, 16GB RAM) | Ephemeral OS Disk (`30GB`) | **$0.00 idle** (~₹25/day active) |
| **Container Storage** | Azure Managed Disk CSI (`4Gi`) | `storageClassName: managed-csi` | **~$0.15 / month** (₹12/mo) |
| **Networking** | Spoke VNet (`10.42.0.0/16`) | **Azure CNI Overlay** | **$0.00 / month** |
| **AI Content Safety** | `cs-ht-bankc-p-sea-01` | `F0` Free Tier (5,000 calls/mo) | **$0.00 / month** |
| **Static Web App** | `stapp-ht-bankc-p-cin-01` | `Free` (`bank.mytaxbot.site`) | **$0.00 / month** |
| **Security Guardrails** | Azure Policy for AKS | OPA Gatekeeper Admission Controller | **$0.00 / month** |

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

Custom domain registration (`bank.mytaxbot.site`) and DNS management are **100% automated as code**:

1. **Dynamic Key Vault Authentication**: Terraform retrieves the Cloudflare API Token dynamically from the central Key Vault (`kv-ht-ss-p-cin-01/secrets/cloudflare-api-token`) via Entra ID RBAC without exposing secrets in code or pipelines.
2. **Automated CNAME Creation**: Resource `cloudflare_record.bankc_cname` automatically creates `bank` ➔ `salmon-ground-xxx.azurestaticapps.net` in Cloudflare's Anycast DNS in < 1 second.
3. **Race Condition Prevention**: Resource `time_sleep.wait_for_dns` introduces an automatic 10-second edge propagation buffer.
4. **Automated Azure SSL Binding**: Resource `azurerm_static_web_app_custom_domain.bankc_custom_domain` binds `bank.mytaxbot.site` to Azure Static Web Apps and automatically issues the free SSL certificate in a **single pass**.
