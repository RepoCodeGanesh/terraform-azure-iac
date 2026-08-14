# Repository Configuration & AI Agent Context

## 🎯 Repository Purpose & Intent
This repository provisions an enterprise-grade **Azure AI Landing Zone** following the **Microsoft Cloud Adoption Framework (CAF)** pattern using **Terraform** and **Azure DevOps CI/CD Pipelines**.

For compact current context, read `docs/PROJECT_CONTEXT.md` first. It preserves the repository goal, current `workloads/tax-advisor` deployment goal, subscription map, recent Terraform fixes, and known apply risks.

---

## 🔑 Subscriptions & Federated Service Connections (WIF)

| Tier / Scope | Azure Subscription Name | Subscription ID | Azure DevOps Service Connection | Workload Target |
| :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | Remote Terraform backend storage (`sthtbootpcin01`) |
| **Hub Network** | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | Hub VNet (`vnet-ht-hub-p-cin-01`) & central routing |
| **Shared Services** | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | Log Analytics, APIM Gateway, Shared Key Vault |
| **Apps (AI Workloads)**| `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | TaxBot India (`workloads/tax-advisor`) & BankCompliance AI (`workloads/bank-compliance-ai-aks`) |

---

## ⚙️ Rules & Architecture Constraints
1. **Multi-Root Terraform State**: Never combine state into a single root. Keep `platform/bootstrap`, `platform/hub`, `platform/shared-services`, `workloads/tax-advisor`, and `workloads/bank-compliance-ai-aks` in separate directories.
2. **Backend Subscription**: All `backend.hcl` files point `subscription_id` to `7689ad81-71ba-481b-a17c-e1b6be61bab1` (where the backend storage account `sthtbootpcin01` lives).
3. **App Deployment**: `workloads/tax-advisor` and `workloads/bank-compliance-ai-aks` deploy resources into `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) and use Azure DevOps service connection `app-prod`.
4. **Cost Optimization**: Default to `Consumption_0`, `F1`, `B1`, and AKS Free Tier with Ephemeral OS to keep running costs near zero when idle (~$0.25/mo).
5. **Pipeline Identity vs Deploy Subscription**: The Azure DevOps service connection determines which identity Terraform uses to authenticate; each root’s `prod.tfvars` `subscription_id` determines where resources are created. Backend `subscription_id` in `backend.hcl` is always the bootstrap subscription for remote state storage only.
6. **Cross-Subscription Terraform**: `workloads/*` uses aliased providers for Hub-prod and Shared-services. The `app-prod` pipeline identity may need RBAC beyond Apps-prod (hub/shared lookups, VNet peering, APIM backend registration in Shared-services).
7. **Terraform Roots vs Reusable Modules**: `platform/*` and `workloads/*` are independent Terraform roots (one state file each), mapped to a home subscription. `modules/` contains subscription-agnostic wrappers invoked by those roots.
