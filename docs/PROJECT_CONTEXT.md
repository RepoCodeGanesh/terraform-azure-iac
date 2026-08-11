# Project Context

This is the compact source of truth for the Azure AI Landing Zone & TaxBot India application repository.

## Repository Goal

Provision an enterprise-style Azure AI Landing Zone using Terraform and Azure DevOps CI/CD, following Microsoft Cloud Adoption Framework patterns while keeping idle cost as close to zero as practical.

Core outcomes:
- Build hands-on Azure DevOps and Terraform IaC practice.
- Create a reusable AI platform foundation for Azure OpenAI, APIM gateway security, telemetry, private networking, and AI Search RAG workloads.
- Host **TaxBot India (AI Income Tax Advisor)** for FY 2026-27 (AY 2027-28).
- Use low-cost SKUs by default: APIM `Consumption`, Functions `Consumption Y1`, Log Analytics `PerGB2018`, Storage `Standard_LRS`, Key Vault `Standard`, Azure OpenAI `S0` with `gpt-5.4-nano`, and Cosmos DB `Serverless`.

## Active Workload Target: TaxBot India (`tax-advisor`)

Deploy and operate `workloads/tax-advisor` and `app/tax-advisor` through Azure DevOps using the `app-prod` service connection.

The workload provisions TaxBot India infrastructure:
- Resource group `rg-ht-taxb-p-cin-01` and spoke VNet `vnet-ht-taxb-p-cin-01` in `Apps-prod`.
- Hub-spoke peering to `vnet-ht-hub-p-cin-01` in `Hub-prod`.
- Azure OpenAI account `oai-ht-taxb-p-eus-01` with `gpt-5.4-nano` deployment.
- Azure AI Search `srch-ht-taxb-p-cin-01` for statutory RAG text retrieval.
- Cosmos DB `cosmos-ht-taxb-p-cin-01` for conversation session state.
- Python Function App `func-ht-taxb-p-cin-01` with system-assigned managed identity.
- Static Web App `stapp-ht-taxb-p-cin-01` bound to custom domain **www.mytaxbot.site**.
- APIM API `apim-ht-ss-p-cin-01` with rate limiting by IP (20 calls/min) and CORS protection.

Current status:
- `platform/bootstrap`: complete.
- `platform/hub`: complete.
- `platform/shared-services`: complete.
- `workloads/tax-advisor`: complete (IaC deployed & active).
- `app/tax-advisor`: complete (React UI + Python backend + APIM rate limiting + custom domain live).
- `pipelines/`: active and verified.

## Subscription Map

| Scope | Subscription | Subscription ID | Azure DevOps Service Connection | Purpose |
| --- | --- | --- | --- | --- |
| Bootstrap | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | Remote Terraform state storage account `sthtbootpcin01` |
| Hub | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | Hub VNet and central routing |
| Shared services | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | Log Analytics, APIM Gateway, Private DNS, Key Vault `kv-ht-ss-p-cin-01` |
| Apps | `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | AI workloads (`workloads/tax-advisor`, `app/tax-advisor`) |

### Entra ID App Registrations & CI/CD Mapping (Workload Identity Federation)

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

1. **Bootstrap Tier** (`bootstrap` subscription: `7689ad81-71ba-481b-a17c-e1b6be61bab1`)
   - **App Registration**: `DevOpsUniverse-Terraform- bootstrap` (Client ID: `934ab83b-2f61-475e-bdbc-85c9eaed83e6`)
   - **Azure DevOps (ADO)**: `pipelines/azure-cicd-bootstrap.yml` using Service Connection `bootstrap`
   - **GitHub Actions**: `.github/workflows/platform-bootstrap.yml` using Secret `BOOTSTRAP_CLIENT_ID`

2. **Hub Network Tier** (`Hub-prod` subscription: `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b`)
   - **App Registration**: `DevOpsUniverse-Terraform- hub-prod` (Client ID: `78960c14-26d2-4a0c-ab21-579c3030155e`)
   - **Azure DevOps (ADO)**: `pipelines/azure-cicd-hub.yml` using Service Connection `hub-prod`
   - **GitHub Actions**: `.github/workflows/platform-hub.yml` using Secret `HUB_CLIENT_ID`

3. **Shared Services Tier** (`Shared-services` subscription: `859a785c-bd38-402d-b595-1f44f40fb9bf`)
   - **App Registration**: `DevOpsUniverse-Terraform-shared-services` (Client ID: `580ffcfd-51ee-4dc3-9204-d03cb438ff82`)
   - **Azure DevOps (ADO)**: `pipelines/azure-cicd-shared-ser.yml` using Service Connection `shared-services`
   - **GitHub Actions**: `.github/workflows/platform-shared-services.yml` using Secret `SHARED_CLIENT_ID`

4. **Apps / AI Workloads Tier** (`Apps-prod` subscription: `f4ffefe1-d689-4059-969c-ccc73e2a11d4`)
   - **App Registration**: `DevOpsUniverse-Terraform-app-prod` (Client ID: `99ab7987-3989-46c3-bae9-92279be16608`)
   - **Azure DevOps (ADO)**: `pipelines/azure-cicd-tax-advisor.yml` & `pipelines/azure-cicd-app-tax-advisor.yml` using Service Connection `app-prod`
   - **GitHub Actions**: `.github/workflows/workload-tax-advisor.yml` & `.github/workflows/app-tax-advisor.yml` using Secret `APP_CLIENT_ID`

## Terraform State Rules

Keep Terraform roots separate. Do not merge state:
- `platform/bootstrap`       → `sthtbootpcin01/tfstate/bootstrap/prod.tfstate`
- `platform/hub`             → `sthtbootpcin01/tfstate/hub/prod.tfstate`
- `platform/shared-services` → `sthtbootpcin01/tfstate/shared-services/prod.tfstate`
- `workloads/tax-advisor`    → `sthtbootpcin01/tfstate/workloads/tax-advisor/prod.tfstate`

## CI/CD Automated Versioning Guide

For details on automated Git release tagging (`v1.0.X`, SemVer rules, commit message conventions), see [docs/AUTOMATED_VERSIONING_GUIDE.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/AUTOMATED_VERSIONING_GUIDE.md).

