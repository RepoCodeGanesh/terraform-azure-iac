# 🏦 BankCompliance AI Workload Infrastructure (`workloads/bank-compliance-ai-aks`)

This directory contains the Terraform infrastructure code for **BankCompliance AI** — an Enterprise Cloud-Native Banking Regulatory & Compliance Copilot provisioned on **Azure Kubernetes Service (AKS)** following Microsoft Cloud Adoption Framework (CAF) patterns.

* **Infrastructure Repository:** [`terraform-azure-iac`](file:///c:/Users/RichT/OneDrive/Documents/Repos/terraform-azure-iac) (`workloads/bank-compliance-ai-aks`)
* **Application Repository:** [`bank-compliance-ai-app`](file:///c:/Users/RichT/OneDrive/Documents/Repos/bank-compliance-ai-app) (`https://github.com/RepoCodeGanesh/bank-compliance-ai-app`)
* **Standalone Architecture Guide:** [docs/BANK_COMPLIANCE_APP_STANDALONE_GUIDE.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/BANK_COMPLIANCE_APP_STANDALONE_GUIDE.md)

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

## 🚀 Deployment Instructions

### 1. Initialize Terraform Backend
```bash
terraform init -backend-config=backend.hcl
```

### 2. Plan Infrastructure
```bash
terraform plan -var-file=prod.tfvars -out=tfplan
```

### 3. Apply Infrastructure
```bash
terraform apply tfplan
```

### 4. Custom Domain Setup (`bank.mytaxbot.site`)
1. Run `terraform apply` with `enable_custom_domain = false` (default).
2. Copy the `static_web_app_default_host_name` output (e.g. `agreeable-beach-xxx.azurestaticapps.net`).
3. In your DNS registrar (where `mytaxbot.site` is managed), add a **CNAME** record:
   * **Host / Name:** `bank`
   * **Points to / Target:** `<static_web_app_default_host_name>`
4. Change `enable_custom_domain = true` in `prod.tfvars` and re-run `terraform apply`.
