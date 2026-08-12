# 📚 Azure AI Landing Zone Documentation Hub

Welcome to the **Azure AI Landing Zone & TaxBot India** documentation repository. This directory contains architectural specifications, subscription maps, CI/CD branching & SemVer guides, and step-by-step operational runbooks.

---

## 🧭 Master Navigation Map

### 1. 🏗️ Architecture & Single Source of Truth
* **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)**: **The primary repository source of truth**. Contains subscription IDs, Entra ID app registrations, dual CI/CD auth mappings (WIF), network CIDR subnets, cost optimization matrix, and multi-root Terraform state rules.

---

### 2. 🔄 CI/CD, Governance & Workflow Guides
* **[BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md)**: Git branching strategy (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`), pull request merge requirements, and environment deployments.
* **[AUTOMATED_VERSIONING_GUIDE.md](AUTOMATED_VERSIONING_GUIDE.md)**: Automated Semantic Versioning (SemVer) guide. Explains how Conventional Commit PR titles (`feat:`, `fix:`, `BREAKING CHANGE:`) drive automatic release tagging (`v1.0.0` $\rightarrow$ `v1.1.0`).
* **[REUSABLE_APP_WORKFLOW_GUIDE.md](REUSABLE_APP_WORKFLOW_GUIDE.md)**: Enterprise Caller/Called Reusable Workflow Pattern guide for GitHub Actions applications. Explains parameterization and integration with central templates in `RepoCodeGanesh/.github`.

---

### 3. 📘 Platform Operations Runbooks (`docs/platform-guide/`)

Detailed step-by-step operational guides for provisioning and operating the Azure AI Landing Zone:

| Runbook File | Description / Topic |
| :--- | :--- |
| **[01-platform-overview.md](platform-guide/01-platform-overview.md)** | High-level landing zone overview, CAF subscriptions, and component topology. |
| **[02-terraform-iac-guide.md](platform-guide/02-terraform-iac-guide.md)** | Multi-root Terraform workflow, backend state storage (`sthtbootpcin01`), and CLI commands. |
| **[03-cicd-pipelines-guide.md](platform-guide/03-cicd-pipelines-guide.md)** | Azure DevOps & GitHub Actions CI/CD pipelines, OIDC/WIF auth, and pipeline sequence diagrams. |
| **[04-naming-and-standards.md](platform-guide/04-naming-and-standards.md)** | Resource naming conventions (CAF pattern `rg-ht-taxb-p-cin-01`), region codes, and tagging rules. |
| **[05-troubleshooting-guide.md](platform-guide/05-troubleshooting-guide.md)** | Known apply risks, Azure OpenAI quota errors, VNet peering locks, and APIM CORS fixes. |
| **[06-blue-green-deployment-guide.md](platform-guide/06-blue-green-deployment-guide.md)** | Zero-downtime Function App & Static Web App deployment strategies. |
| **[07-monitoring-telemetry-guide.md](platform-guide/07-monitoring-telemetry-guide.md)** | Application Insights, Log Analytics queries, and APIM request rate limiting telemetry. |

---

### 4. 🧱 Component-Level Technical Documentation

* **[Platform Infrastructure README](../platform/README.md)**: `platform/bootstrap`, `platform/hub`, and `platform/shared-services` Terraform roots.
* **[Workload Infrastructure README](../workloads/README.md)**: `workloads/tax-advisor` TaxBot India infrastructure specification.
* **[Azure DevOps Pipelines README](../pipelines/README.md)**: Azure DevOps pipeline YAML specifications.
