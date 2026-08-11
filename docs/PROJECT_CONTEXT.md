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

## Subscription Map & Entra ID Service Principal (WIF) Inventory

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

| Scope | App Registration Name | Application (Client) ID | Object ID | Subscription Name & ID | ADO Connection | GitHub Secret | GitHub OIDC Subject |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `DevOpsUniverse-Terraform- bootstrap` | `934ab83b-2f61-475e-bdbc-85c9eaed83e6` | `18409448-e4a2-44d6-b183-9f6078f8cca9` | `bootstrap`<br>`7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | `BOOTSTRAP_CLIENT_ID` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:bootstrap-prod` |
| **Hub Network** | `DevOpsUniverse-Terraform- hub-prod` | `78960c14-26d2-4a0c-ab21-579c3030155e` | `53c050aa-35b4-44fe-b5a7-be9534de76f4` | `Hub-prod`<br>`3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | `HUB_CLIENT_ID` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:hub-prod` |
| **Shared Services** | `DevOpsUniverse-Terraform-shared-services` | `580ffcfd-51ee-4dc3-9204-d03cb438ff82` | `95b2158a-b8a5-443c-8d37-c8eae790363d` | `Shared-services`<br>`859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | `SHARED_CLIENT_ID` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:shared-services-prod` |
| **Apps (AI Workloads)** | `DevOpsUniverse-Terraform-app-prod` | `99ab7987-3989-46c3-bae9-92279be16608` | `418b13c5-39a6-4be7-9ad4-fe57b49b0f67` | `Apps-prod`<br>`f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | `APP_CLIENT_ID` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:tax-advisor-prod` |

## Terraform State Rules

Keep Terraform roots separate. Do not merge state:
- `platform/bootstrap`       → `sthtbootpcin01/tfstate/bootstrap/prod.tfstate`
- `platform/hub`             → `sthtbootpcin01/tfstate/hub/prod.tfstate`
- `platform/shared-services` → `sthtbootpcin01/tfstate/shared-services/prod.tfstate`
- `workloads/tax-advisor`    → `sthtbootpcin01/tfstate/workloads/tax-advisor/prod.tfstate`
