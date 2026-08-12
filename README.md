# Azure AI Landing Zone

Terraform and Azure DevOps infrastructure for a low-cost Azure AI landing zone.

This repo builds a CAF-style multi-subscription platform for Azure AI workloads, with separate Terraform state per layer, Workload Identity Federation in Azure DevOps, hub-spoke networking, shared telemetry/APIM services, and an active `workloads/tax-advisor` deployment.

Start here:
- [docs/README.md](docs/README.md) - **Master Documentation Hub** (Table of Contents for Architecture, CI/CD, Platform Runbooks, and Standards).
- [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) - Canonical project context, subscription map, deployment sequence, and cost matrix.
- [docs/platform-guide/README.md](docs/platform-guide/README.md) - Platform Guide Visual Documentation Suite (Mermaid topology, IaC guide, CI/CD pipelines, CAF naming, Blue-Green deployments, & telemetry).
- [AGENTS.md](AGENTS.md) - Concise rules for AI agents working in this repository.

## Terraform Roots

Deploy roots independently and in this order:

1. `platform/bootstrap`
2. `platform/hub`
3. `platform/shared-services`
4. `workloads/tax-advisor`

Do not merge these roots into one Terraform state.

## Current Work

The active goal is operating `workloads/tax-advisor` (TaxBot India) through the `app-prod` Azure DevOps service connection.

Key workload notes:
- Main workload region: `centralindia` / `cin`
- Azure OpenAI region: `eastus` / `eus`
- Function App plan: workload-local `Y1` consumption plan
- Model deployment: `gpt-5.4-nano`
- Custom domain: `www.mytaxbot.site`

## Validate Locally

From a Terraform root:

```bash
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
```

Use the pipeline for backend-enabled plan/apply.
