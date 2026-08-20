# Azure AI Landing Zone

[![GitHub Stars](https://img.shields.io/github/stars/RepoCodeGanesh/terraform-azure-iac?style=social)](https://github.com/RepoCodeGanesh/terraform-azure-iac)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-purple.svg)](https://www.terraform.io/)
[![Azure CAF](https://img.shields.io/badge/Architecture-Azure%20CAF-0078D4.svg)](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/)
[![TaxBot India](https://img.shields.io/badge/Live-mytaxbot.site-brightgreen.svg)](https://www.mytaxbot.site)
[![BankCompliance AI](https://img.shields.io/badge/Live-bank.mytaxbot.site-blue.svg)](https://bank.mytaxbot.site)
[![Confluence Wiki](https://img.shields.io/badge/Confluence-HappyTechies%20Wiki-0052CC.svg)](https://happytechies.atlassian.net/wiki/spaces/HT/overview)

Terraform and Azure DevOps infrastructure for an enterprise-grade, low-cost Azure AI landing zone.

This repo builds a CAF-style multi-subscription platform for Azure AI workloads, with separate Terraform state per layer, Workload Identity Federation in Azure DevOps & GitHub Actions, hub-spoke networking, shared telemetry/APIM services, and dual production AI workloads.

Start here:
- [docs/README.md](docs/README.md) - **Master Documentation Hub** (Architecture, CI/CD, Platform Runbooks, and Standards).
- [docs/confluence/README.md](docs/confluence/README.md) - **Confluence Wiki Suite** ([Live on Atlassian](https://happytechies.atlassian.net/wiki/spaces/HT/overview)).
- [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) - Canonical project context, subscription map, deployment sequence, and cost matrix.
- [docs/platform-guide/README.md](docs/platform-guide/README.md) - Platform Guide Visual Documentation Suite (Mermaid topology, IaC guide, CI/CD pipelines, CAF naming, Blue-Green deployments, & telemetry).
- [AGENTS.md](AGENTS.md) - Concise rules for AI agents working in this repository.

## Terraform Roots

Deploy roots independently and in this order:

1. `platform/bootstrap`
2. `platform/hub`
3. `platform/shared-services`
4. `workloads/tax-advisor` (TaxBot India — Serverless PaaS on [www.mytaxbot.site](https://www.mytaxbot.site))
5. `workloads/bank-compliance-ai-aks` (BankCompliance AI — AKS Free Tier on [bank.mytaxbot.site](https://bank.mytaxbot.site))

Do not merge these roots into one Terraform state.

## Decoupled Applications

* **TaxBot India App:** Located in `app/tax-advisor` (React SPA + Python Functions).
* **BankCompliance AI App:** Standalone external repository [`bank-compliance-ai-app`](https://github.com/RepoCodeGanesh/bank-compliance-ai-app) (FastAPI + React SPA + Qdrant 4GB CSI + LiteLLM Gateway). See [Standalone App Guide](docs/BANK_COMPLIANCE_APP_STANDALONE_GUIDE.md).

## Validate Locally

From a Terraform root:

```bash
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
```

Use the pipeline for backend-enabled plan/apply.

---

## ⭐ Support & Star

If you find this Enterprise Azure AI Landing Zone repository useful, please give it a **⭐ Star** on GitHub! It helps increase visibility and supports open-source enterprise IaC templates.
