# Azure DevOps CI/CD Pipelines

This directory contains the Azure DevOps YAML pipeline workflows and reusable stage templates for automated Terraform validation, planning, and deployment across your Enterprise Azure Landing Zone.

---

## 📂 Folder Structure

```
pipelines/
├── README.md                      # This documentation file
├── azure-cicd-bootstrap.yml       # Pipeline for platform/bootstrap
├── azure-cicd-hub.yml             # Pipeline for platform/hub
├── azure-cicd-shared-ser.yml      # Pipeline for platform/shared-services
├── azure-cicd-tax-advisor.yml     # Pipeline for workloads/tax-advisor
├── azure-cicd-app-tax-advisor.yml # Pipeline for app/tax-advisor
├── azure-cicd-bank-compliance-aks.yml # Pipeline for workloads/bank-compliance-ai-aks
├── azure-cicd-app-bank-compliance.yml # Pipeline for app/bank-compliance (DevSecOps + AKS + SWA)
└── templates/                     # Reusable pipeline stage templates
    ├── validate.yml               # Optional standalone validate stage
    ├── plan.yml                   # Format check, validation & speculative terraform plan
    └── apply.yml                  # Terraform apply with environment approvals
```

---

## ⚡ Key Pipeline Architecture & Features

### 1. Monorepo Path Filtering
Pipelines are configured with **Path Filtering** (`paths: include/exclude`) to ensure that changes in one infrastructure layer only trigger its specific pipeline:
* **Bootstrap Changes** (`platform/bootstrap/**`) ➔ Triggers `azure-cicd-bootstrap.yml`
* **Hub Changes** (`platform/hub/**`) ➔ Triggers `azure-cicd-hub.yml`
* **Shared Services Changes** (`platform/shared-services/**`) ➔ Triggers `azure-cicd-shared-ser.yml`
* **TaxBot Workload Changes** (`workloads/tax-advisor/**`) ➔ Triggers `azure-cicd-tax-advisor.yml`
* **TaxBot Application Changes** (`app/tax-advisor/**`) ➔ Triggers `azure-cicd-app-tax-advisor.yml`
* **BankCompliance Workload Changes** (`workloads/bank-compliance-ai-aks/**`) ➔ Triggers `azure-cicd-bank-compliance-aks.yml`
* **BankCompliance Application Changes** (`app/bank-compliance/**`) ➔ Triggers `azure-cicd-app-bank-compliance.yml`
* **Documentation Edits** (`**/*.md`) ➔ **Excluded** from triggering builds to preserve agent minutes.

---

### Service connections & Terraform roots

Each pipeline uses **Azure Resource Manager** authentication via **Workload Identity federation**. The service connection name must match the pipeline variable exactly.

| Azure DevOps service connection | Pipeline YAML | Terraform root | Home subscription |
| :--- | :--- | :--- | :--- |
| `bootstrap` | `azure-cicd-bootstrap.yml` | `platform/bootstrap` | `bootstrap` (`7689ad81-71ba-481b-a17c-e1b6be61bab1`) |
| `hub-prod` | `azure-cicd-hub.yml` | `platform/hub` | `Hub-prod` (`3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b`) |
| `shared-services` | `azure-cicd-shared-ser.yml` | `platform/shared-services` | `Shared-services` (`859a785c-bd38-402d-b595-1f44f40fb9bf`) |
| `app-prod` | `azure-cicd-tax-advisor.yml` | `workloads/tax-advisor` | `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) |
| `app-prod` | `azure-cicd-bank-compliance-aks.yml` | `workloads/bank-compliance-ai-aks` | `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) |


**Remote state backend:** All roots store state in the bootstrap storage account `sthtbootpcin01`. Every pipeline identity needs **Storage Blob Data** access on that account (or container) for `terraform init` / plan / apply, even when deploying into another subscription.

**Cross-subscription:** The `app-prod` connection deploys into Apps-prod but Terraform also reads Hub-prod and Shared-services (peering, shared ASP/LAW/APIM) and may write APIM backends in Shared-services. Grant the federated identity RBAC on those scopes as needed.

---

### 2. PR Validation vs. Merged Execution

* **Pull Requests (`feature/*` ➔ `develop` / `main`)**:
  * Runs **Plan Stage** (includes `terraform fmt -check`, `terraform validate`, and speculative `terraform plan`).
  * Exports JSON plan artifact for review.
  * **Apply Stage is automatically skipped** on Pull Requests to protect target infrastructure.

* **Branch Merges / Direct Commits (`develop` / `main`)**:
  * Runs **Plan Stage**.
  * Executes **Apply Stage** (`terraform apply -auto-approve tfplan.binary`) using the saved plan artifact.

---

### 3. Azure DevOps Environment Approvals

Deployment jobs in `apply.yml` bind to specific Azure DevOps Environments:
* `bootstrap-prod`
* `hub-prod`
* `shared-services-prod`
* `tax-advisor-prod`

To enable **Manual Approval Gates**, navigate to **Azure DevOps ➔ Pipelines ➔ Environments**, select the environment, and configure **Approvals and checks**.

---

### 4. Performance & Caching Optimizations

* **Provider Caching (`Cache@2`)**: Shared cross-layer cache key (`terraform-providers | "$(Agent.OS)"`) prevents re-downloading AzureRM provider binaries.
* **Stage Consolidation**: Validation logic runs inside the `Plan` stage VM, eliminating unnecessary VM boot overhead.
