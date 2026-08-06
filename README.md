# Azure AI Landing Zone

Terraform and Azure DevOps infrastructure for a low-cost Azure AI landing zone.

This repo builds a CAF-style multi-subscription platform for Azure AI workloads, with separate Terraform state per layer, Workload Identity Federation in Azure DevOps, hub-spoke networking, shared telemetry/APIM services, and an active `workloads/ai-assistant` deployment.

Start here:
- [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) - canonical project context, architecture, deployment order, current goal, and troubleshooting notes.
- [AGENTS.md](AGENTS.md) - concise rules for Codex/AI agents working in this repo.

## Terraform Roots

Deploy roots independently and in this order:

1. `platform/bootstrap`
2. `platform/hub`
3. `platform/shared-services`
4. `workloads/ai-assistant`

Do not merge these roots into one Terraform state.

## Current Work

The active goal is stabilizing and deploying `workloads/ai-assistant` through the `app-prod` Azure DevOps service connection.

Key workload notes:
- Main workload region: `centralindia` / `cin`
- Azure OpenAI region: `southindia` / `sin`
- Function App plan: workload-local `Y1` consumption plan
- Model deployment: `gpt-4o-mini` version `2024-07-18`

## Validate Locally

From a Terraform root:

```bash
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
```

Use the pipeline for backend-enabled plan/apply.
