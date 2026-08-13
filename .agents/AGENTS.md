# Repository Configuration & AI Agent Context

## 🎯 Repository Purpose & Intent
This repository provisions an enterprise-grade **Azure AI Landing Zone** following the **Microsoft Cloud Adoption Framework (CAF)** pattern using **Terraform** and **Dual CI/CD Pipelines (Azure DevOps & GitHub Actions)**.

For compact current context, read `docs/PROJECT_CONTEXT.md` first. It preserves the repository goal, current `workloads/tax-advisor` deployment goal, subscription map, recent Terraform fixes, and known apply risks.

---

## 🔑 Subscriptions & Dual CI/CD Authentication (Workload Identity Federation)

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

| Tier / Scope | Azure Subscription | Azure DevOps (ADO) Pipeline & Connection | GitHub Actions Workflow & Secret | Entra ID App Registration (Client ID) |
| :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `bootstrap`<br>`7689ad81-71ba-481b-a17c-e1b6be61bab1` | `pipelines/azure-cicd-bootstrap.yml`<br>Service Connection: `bootstrap` | `.github/workflows/platform-bootstrap.yml`<br>Secret: `BOOTSTRAP_CLIENT_ID` | `DevOpsUniverse-Terraform-bootstrap`<br>`934ab83b-2f61-475e-bdbc-85c9eaed83e6` |
| **Hub Network** | `Hub-prod`<br>`3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `pipelines/azure-cicd-hub.yml`<br>Service Connection: `hub-prod` | `.github/workflows/platform-hub.yml`<br>Secret: `HUB_CLIENT_ID` | `DevOpsUniverse-Terraform-hub-prod`<br>`78960c14-26d2-4a0c-ab21-579c3030155e` |
| **Shared Services** | `Shared-services`<br>`859a785c-bd38-402d-b595-1f44f40fb9bf` | `pipelines/azure-cicd-shared-ser.yml`<br>Service Connection: `shared-services` | `.github/workflows/platform-shared-services.yml`<br>Secret: `SHARED_CLIENT_ID` | `DevOpsUniverse-Terraform-shared-services`<br>`580ffcfd-51ee-4dc3-9204-d03cb438ff82` |
| **Apps (AI Workloads)** | `Apps-prod`<br>`f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `pipelines/azure-cicd-app-tax-advisor.yml`<br>Service Connection: `app-prod` | `.github/workflows/app-tax-advisor.yml`<br>Secret: `APP_CLIENT_ID` | `DevOpsUniverse-Terraform-app-prod`<br>`99ab7987-3989-46c3-bae9-92279be16608` |

---

## ⚙️ Rules & Architecture Constraints
1. **Multi-Root Terraform State**: Never combine state into a single root. Keep `platform/bootstrap`, `platform/hub`, `platform/shared-services`, and `workloads/tax-advisor` in separate directories.
2. **Backend Subscription**: All `backend.hcl` files point `subscription_id` to `7689ad81-71ba-481b-a17c-e1b6be61bab1` (where the backend storage account `sthtbootpcin01` lives).
3. **App Deployment**: `workloads/tax-advisor` deploys resources into `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) and uses Azure DevOps service connection `app-prod` or GitHub Actions WIF `tax-advisor-prod`.
4. **Cost Optimization**: Default to `Consumption_0`, `F1`, `B1`, and Cosmos DB Manual `400 RU/s` (Free Tier) to keep running costs near zero when idle.
5. **Central Called Workflows**: App deployments delegate execution to central reusable templates in `RepoCodeGanesh/.github` across 4 parallelized phases.
6. **WIF OIDC Claim Rule**: GitHub Actions workflows using Entra ID identity `DevOpsUniverse-Terraform-app-prod` must specify `environment: tax-advisor-prod` to match federated credential claims.
7. **Observability**: Stream logs from Azure OpenAI, AI Search, Cosmos DB, and Functions into central Log Analytics `law-ht-ss-p-cin-01` via `azurerm_monitor_diagnostic_setting`.
