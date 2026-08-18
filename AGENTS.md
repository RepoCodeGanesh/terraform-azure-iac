# Repository Configuration & AI Agent Context

## Purpose
This is the **Enterprise Azure Landing Zone monorepo** for HappyTechies Cloud & AI Platform.
It contains all Terraform infrastructure, Azure DevOps pipelines, and application code for all workloads.

---

## Workspace Layout

```
terraform-azure-iac/
├── platform/
│   ├── bootstrap/          # Bootstrap sub (7689ad81) — remote state SA, Key Vault
│   ├── hub/                # Hub-prod sub (3eb8cc01) — Azure Firewall, Bastion, Gateway
│   └── shared-services/    # Shared-services sub (859a785c) — APIM, Log Analytics, Key Vault
├── workloads/
│   ├── tax-advisor/        # TaxBot IaC — Apps-prod sub (f4ffefe1)
│   └── bank-compliance-ai-aks/ # BankCompliance IaC — Apps-prod sub (f4ffefe1)
├── app/
│   ├── tax-advisor/        # TaxBot app code (React + Python Function App)
│   └── bank-compliance/    # BankCompliance app code (React + FastAPI + k8s manifests)
│       ├── backend/        # FastAPI backend + Dockerfile
│       ├── frontend/       # React Vite SPA (bank.mytaxbot.site)
│       ├── k8s/            # All Kubernetes manifests (namespace, SA, deployments, KEDA)
│       └── .github/workflows/ # GitHub Actions CI/CD
├── modules/                # Reusable Terraform modules
├── pipelines/              # Azure DevOps pipeline YAMLs + reusable templates
└── docs/                   # Architecture docs, guides, planning docs
```

---

## Subscription Map

| Scope | Subscription | Subscription ID |
|-------|-------------|----------------|
| Bootstrap | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` |
| Hub Network | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` |
| Shared Services | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` |
| Apps / AI Workloads | `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` |

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

---

## Active Workloads

### Workload 1: TaxBot India
- **Domain:** https://www.mytaxbot.site
- **IaC:** `workloads/tax-advisor/`
- **App:** `app/tax-advisor/`
- **CI/CD:** `pipelines/azure-cicd-tax-advisor.yml` + `.github/workflows/`

### Workload 2: BankCompliance AI
- **Domain:** https://bank.mytaxbot.site
- **IaC:** `workloads/bank-compliance-ai-aks/`
- **App:** `app/bank-compliance/` (migrated from standalone repo — same pattern as tax-advisor)
- **CI/CD:** `pipelines/azure-cicd-bank-compliance-aks.yml` + `app/bank-compliance/.github/workflows/build-and-deploy.yml`
- **Stack:** AKS Free Tier (`aks-ht-bankc-p-cin-01`), LiteLLM Proxy, Qdrant (4GB CSI disk), KEDA scale-to-zero
- **Key IaC Outputs needed by app:**
  - `aks_workload_identity_client_id` → annotate `k8s/serviceaccount.yaml`
  - `content_safety_endpoint` → set in `k8s/backend-configmap.yaml`
  - `static_web_app_api_key` → GitHub Secret `AZURE_STATIC_WEB_APPS_API_TOKEN`

---

## CI/CD Authentication (Workload Identity Federation)

| ADO Service Connection | GitHub Secret | App Registration Client ID | Enterprise App Object ID (Principal ID) |
|----------------------|---------------|---------------------------|------------------------------------------|
| `bootstrap` | `BOOTSTRAP_CLIENT_ID` | `934ab83b-2f61-475e-bdbc-85c9eaed83e6` | `f3a1b19b-11b8-4e13-8499-7f83ea39547a` |
| `hub-prod` | `HUB_CLIENT_ID` | `78960c14-26d2-4a0c-ab21-579c3030155e` | `14cfc7b4-c3a2-4994-9f5c-0ce4d8db0f57` |
| `shared-services` | `SHARED_CLIENT_ID` | `580ffcfd-51ee-4dc3-9204-d03cb438ff82` | `c5a24473-2bad-41a7-b0b1-b79b94621252` |
| `app-prod` | `APP_CLIENT_ID` | `99ab7987-3989-46c3-bae9-92279be16608` | `9630f661-27e7-42f0-8377-5565ba7db7cd` |

GitHub Secrets required for BankCompliance GHA: `APP_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_STATIC_WEB_APPS_API_TOKEN`

---

## Terraform State (Remote — Azure Blob)

All roots use Azure AD auth (`use_azuread_auth = true`) against `sthtbootpcin01` in the bootstrap subscription.
State files are path-keyed — **git repo location does not affect state**.

| Root | State Key |
|------|-----------|
| `platform/bootstrap` | `bootstrap/prod.tfstate` |
| `platform/hub` | `hub/prod.tfstate` |
| `platform/shared-services` | `shared-services/prod.tfstate` |
| `workloads/tax-advisor` | `workloads/tax-advisor/prod.tfstate` |
| `workloads/bank-compliance-ai-aks` | `workloads/bank-compliance-ai-aks/prod.tfstate` |

---

## Agent Rules

1. When working on `app/bank-compliance/`, always cross-check `workloads/bank-compliance-ai-aks/outputs.tf` for resource names and endpoints that must be wired into k8s ConfigMaps.
2. Never hardcode subscription IDs — use `${{ secrets.AZURE_SUBSCRIPTION_ID }}` in GHA and `var.subscription_id` in Terraform.
3. Terraform roots are independent — do not merge state files or add cross-root `terraform_remote_state` without explicit instruction.
4. The ADO environment for BankCompliance infra approvals is `bank-compliance-prod`. Do not use `tax-advisor-prod`.
5. LiteLLM image must be pinned to a specific version tag — never use `:main-latest`.