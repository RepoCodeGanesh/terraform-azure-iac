# Azure DevOps CI/CD Pipelines

This directory contains the Azure DevOps YAML pipeline workflows and reusable stage templates for automated Terraform validation, planning, and deployment across your Enterprise Azure Landing Zone.

---

## 📂 Folder Structure

```
pipelines/
├── README.md                                       # This documentation file
├── azure-cicd-platform-governance.yml             # Pipeline for platform/governance (Root MG & Policy-as-Code)
├── azure-cicd-platform-bootstrap.yml              # Pipeline for platform/bootstrap (Remote state & Key Vault)
├── azure-cicd-platform-hub.yml                    # Pipeline for platform/hub (Firewall & Hub VNet)
├── azure-cicd-platform-shared-services.yml        # Pipeline for platform/shared-services (APIM, LAW, AI)
├── azure-cicd-workload-tax-advisor.yml            # Pipeline for workloads/tax-advisor (IaC)
├── azure-cicd-workload-bank-compliance-aks.yml    # Pipeline for workloads/bank-compliance-ai-aks (IaC)
├── azure-cicd-app-tax-advisor.yml                 # Pipeline for app/tax-advisor (React + Python Functions)
├── azure-cicd-app-bank-compliance.yml             # Pipeline for app/bank-compliance (DevSecOps + AKS + SWA)
├── azure-cicd-mlops-lora-training.yml             # Pipeline for decoupled LoRA/PEFT Fine-Tuning & Eval
├── azure-cicd-ops-drift-detection.yml             # Pipeline for automated daily multi-root drift detection
├── azure-cicd-finops-aks-auto-shutdown.yml        # Pipeline for nightly AKS auto-shutdown (FinOps $0.00)
└── templates/                                     # Reusable pipeline stage templates
    ├── validate.yml                               # Optional standalone validate stage
    ├── plan.yml                                   # Format check, validation & speculative terraform plan
    └── apply.yml                                  # Terraform apply with environment approvals
```

---

## ⚡ Key Pipeline Architecture & Features

### 1. Monorepo Path Filtering
Pipelines are configured with **Path Filtering** (`paths: include/exclude`) to ensure that changes in one infrastructure layer only trigger its specific pipeline:
* **Governance Changes** (`platform/governance/**`) ➔ Triggers `azure-cicd-platform-governance.yml`
* **Bootstrap Changes** (`platform/bootstrap/**`) ➔ Triggers `azure-cicd-platform-bootstrap.yml`
* **Hub Changes** (`platform/hub/**`) ➔ Triggers `azure-cicd-platform-hub.yml`
* **Shared Services Changes** (`platform/shared-services/**`) ➔ Triggers `azure-cicd-platform-shared-services.yml`
* **TaxBot Workload Changes** (`workloads/tax-advisor/**`) ➔ Triggers `azure-cicd-workload-tax-advisor.yml`
* **TaxBot Application Changes** (`app/tax-advisor/**`) ➔ Triggers `azure-cicd-app-tax-advisor.yml`
* **BankCompliance Workload Changes** (`workloads/bank-compliance-ai-aks/**`) ➔ Triggers `azure-cicd-workload-bank-compliance-aks.yml`
* **BankCompliance Application Changes** (`app/bank-compliance/**`) ➔ Triggers `azure-cicd-app-bank-compliance.yml`
* **Documentation Edits** (`**/*.md`) ➔ **Excluded** from triggering builds to preserve agent minutes.

---

### Service Connections & Terraform Roots

Each pipeline uses **Azure Resource Manager** authentication via **Workload Identity Federation**. The service connection name must match the pipeline variable exactly.

| Azure DevOps Service Connection | Pipeline YAML | Terraform Root | Target Scope |
| :--- | :--- | :--- | :--- |
| `bootstrap` | `azure-cicd-platform-governance.yml` | `platform/governance` | `HappieTechies-root-MG` (Root MG) |
| `bootstrap` | `azure-cicd-platform-bootstrap.yml` | `platform/bootstrap` | `bootstrap` (`7689ad81-71ba-481b-a17c-e1b6be61bab1`) |
| `hub-prod` | `azure-cicd-platform-hub.yml` | `platform/hub` | `Hub-prod` (`3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b`) |
| `shared-services` | `azure-cicd-platform-shared-services.yml` | `platform/shared-services` | `Shared-services` (`859a785c-bd38-402d-b595-1f44f40fb9bf`) |
| `app-prod` | `azure-cicd-workload-tax-advisor.yml` | `workloads/tax-advisor` | `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) |
| `app-prod` | `azure-cicd-workload-bank-compliance-aks.yml` | `workloads/bank-compliance-ai-aks` | `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) |

**Remote state backend:** All roots store state in the bootstrap storage account `sthtbootpcin01`. Every pipeline identity needs **Storage Blob Data** access on that account (or container) for `terraform init` / plan / apply.

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
* `bank-compliance-prod`

To enable **Manual Approval Gates**, navigate to **Azure DevOps ➔ Pipelines ➔ Environments**, select the environment, and configure **Approvals and checks**.
