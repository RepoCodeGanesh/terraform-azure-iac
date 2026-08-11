# Repository Configuration & AI Agent Context

## 🎯 Repository Purpose & Intent
This repository provisions an enterprise-grade **Azure AI Landing Zone** following the **Microsoft Cloud Adoption Framework (CAF)** pattern using **Terraform** and **Azure DevOps CI/CD Pipelines**.

---

## 🔑 Subscriptions & Service Principals (Workload Identity Federation)

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

| Tier / Scope | App Registration Name | Application (Client) ID | Object ID | Azure Subscription | Subscription ID | ADO Service Connection | GitHub Secret |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `DevOpsUniverse-Terraform- bootstrap` | `934ab83b-2f61-475e-bdbc-85c9eaed83e6` | `18409448-e4a2-44d6-b183-9f6078f8cca9` | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | `BOOTSTRAP_CLIENT_ID` |
| **Hub Network** | `DevOpsUniverse-Terraform- hub-prod` | `78960c14-26d2-4a0c-ab21-579c3030155e` | `53c050aa-35b4-44fe-b5a7-be9534de76f4` | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | `HUB_CLIENT_ID` |
| **Shared Services** | `DevOpsUniverse-Terraform-shared-services` | `580ffcfd-51ee-4dc3-9204-d03cb438ff82` | `95b2158a-b8a5-443c-8d37-c8eae790363d` | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | `SHARED_CLIENT_ID` |
| **Apps (AI Workloads)**| `DevOpsUniverse-Terraform-app-prod` | `99ab7987-3989-46c3-bae9-92279be16608` | `418b13c5-39a6-4be7-9ad4-fe57b49b0f67` | `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | `APP_CLIENT_ID` |

---

## ⚙️ Rules & Architecture Constraints
1. **Multi-Root Terraform State**: Never combine state into a single root. Keep `platform/bootstrap`, `platform/hub`, `platform/shared-services`, and `workloads/tax-advisor` in separate directories.
2. **Backend Subscription**: All `backend.hcl` files point `subscription_id` to `7689ad81-71ba-481b-a17c-e1b6be61bab1` (where the backend storage account `sthtbootpcin01` lives).
3. **App Deployment**: `workloads/tax-advisor` deploys resources into `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) and uses Azure DevOps service connection `app-prod`.
4. **Cost Optimization**: Default to `Consumption_0`, `F1`, and `B1` SKUs to keep running costs near zero when idle.
5. **Pipeline Identity vs Deploy Subscription**: The Azure DevOps service connection determines which identity Terraform uses to authenticate; each root’s `prod.tfvars` `subscription_id` determines where resources are created. Backend `subscription_id` in `backend.hcl` is always the bootstrap subscription for remote state storage only.
6. **Cross-Subscription Terraform**: `workloads/tax-advisor` uses aliased providers for Hub-prod and Shared-services. The `app-prod` pipeline identity may need RBAC beyond Apps-prod (hub/shared lookups, VNet peering, APIM backend registration in Shared-services).
7. **Terraform Roots vs Reusable Modules**: `platform/*` and `workloads/*` are independent Terraform roots (one state file each), mapped to a home subscription. `modules/` contains subscription-agnostic wrappers invoked by those roots.
