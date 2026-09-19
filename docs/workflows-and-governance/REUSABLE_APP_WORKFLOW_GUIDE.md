# Enterprise Reusable Application CI/CD Workflow Guide

## 🎯 Overview & Design Pattern

This document defines the **Enterprise Parameterized Reusable Workflow Pattern** for application deployments.

By extracting generic, multi-stage application build and deployment steps into central reusable workflows inside the `RepoCodeGanesh/.github` repository, application repositories (e.g. `app-tax-advisor`) function as clean, lightweight **caller workflows** passing only application-specific parameters.

---

## 🏗️ Parallelized Caller vs. Called Architecture

To optimize pipeline execution speed, independent build, deployment, and document sync jobs run **in parallel** during Phase 2 as soon as security scanning completes.

```mermaid
flowchart TD
    subgraph Phase1["Phase 1: DevSecOps Scanning"]
        T1["app-sec-scan.yml<br/>(Bandit, pip-audit, npm audit, SonarCloud)"]
    end

    subgraph Phase2["Phase 2: ⚡ Parallel Build, Deploy & Sync"]
        T2["app-deploy-func.yml<br/>(Python ZipDeploy + Healthcheck)"]
        T3["app-deploy-swa.yml<br/>(Node 22 React Build + SWA Upload)"]
        T4["app-sync-docs.yml<br/>(RAG Document Sync to Blob Storage)"]
    end

    subgraph Phase3["Phase 3: CORS & Network Configuration"]
        T5["app-config-cors.yml<br/>(SWA Hostname & Function App CORS)"]
    end

    subgraph Phase4["Phase 4: Enterprise Release & Tagging"]
        T6["app-tag-semver.yml<br/>(GitHub Tag Action + SemVer Release)"]
    end

    T1 -->|needs: devsecops-scan| T2
    T1 -->|needs: devsecops-scan| T3
    T1 -->|needs: devsecops-scan| T4

    T2 -->|needs: [deploy-backend, deploy-frontend]| T5
    T3 -->|needs: [deploy-backend, deploy-frontend]| T5

    T5 -->|needs: [configure-cors, upload-documents]| T6
    T4 -->|needs: [configure-cors, upload-documents]| T6
```

---

## 🧩 Central Reusable Templates Specification (`RepoCodeGanesh/.github`)

| Central Workflow File | Purpose | Parameters / Inputs |
| :--- | :--- | :--- |
| **`app-sec-scan.yml`** | SAST & SCA security scanning (Bandit, pip-audit, SonarCloud) | `working_directory`, `key_vault_name`, `shared_subscription_id` |
| **`app-deploy-func.yml`** | Packages Python Function App & deploys via ZipDeploy | `function_app_name`, `working_directory`, `app_subscription_id` |
| **`app-sync-docs.yml`** | Syncs local RAG text documents to Blob Storage using RBAC | `storage_account_name`, `container_name`, `source_directory`, `app_subscription_id`, `environment_name` |
| **`app-deploy-swa.yml`** | Builds React SPA & deploys to Azure Static Web App | `static_web_app_name`, `working_directory`, `key_vault_name`, `shared_subscription_id` |
| **`app-config-cors.yml`** | Fetches SWA hostname & updates Function App CORS origins | `static_web_app_name`, `function_app_name`, `resource_group`, `app_subscription_id`, `environment_name` |
| **`app-tag-semver.yml`** | Generates SemVer git tag & creates GitHub release with artifacts | `artifact_name`, `release_artifacts`, `default_bump`, `tag_prefix` |

---

## 💻 Parallelized Caller Workflow Specification (`app-tax-advisor.yml`)

When refactored into a parallelized **Caller Workflow**, `app-tax-advisor.yml` achieves 50% faster deployment times:

```yaml
name: App - TaxBot India CI/CD

on:
  push:
    branches: [main, develop, 'feature/**', 'release/**', 'hotfix/**']
    tags: ['release/*', 'v*']
    paths:
      - 'app/tax-advisor/**'
      - '.github/workflows/app-tax-advisor.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'app/tax-advisor/**'
  workflow_dispatch:

permissions:
  id-token: write
  contents: write

jobs:
  # ── JOB 0: DevSecOps SAST & SCA Security Scanning (Phase 1) ────────────────
  devsecops-scan:
    name: DevSecOps SAST & SCA Scan
    uses: RepoCodeGanesh/.github/.github/workflows/app-sec-scan.yml@main
    with:
      working_directory: 'app/tax-advisor'
      key_vault_name: 'kv-ht-ss-p-cin-01'
      shared_subscription_id: '859a785c-bd38-402d-b595-1f44f40fb9bf'
    secrets:
      SHARED_CLIENT_ID: ${{ secrets.SHARED_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

  # ── JOB 1: Deploy Python Backend Function App (Phase 2 - Parallel) ─────────
  deploy-backend:
    name: Deploy Python Function App Backend
    needs: devsecops-scan
    uses: RepoCodeGanesh/.github/.github/workflows/app-deploy-func.yml@main
    with:
      function_app_name: 'func-ht-taxb-p-cin-01'
      working_directory: 'app/tax-advisor/backend'
      app_subscription_id: 'f4ffefe1-d689-4059-969c-ccc73e2a11d4'
    secrets:
      APP_CLIENT_ID: ${{ secrets.APP_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

  # ── JOB 2: Build & Deploy React Frontend SPA (Phase 2 - Parallel) ──────────
  deploy-frontend:
    name: Build & Deploy React Frontend
    needs: devsecops-scan
    uses: RepoCodeGanesh/.github/.github/workflows/app-deploy-swa.yml@main
    with:
      static_web_app_name: 'stapp-ht-taxb-p-cin-01'
      working_directory: 'app/tax-advisor/frontend'
      key_vault_name: 'kv-ht-ss-p-cin-01'
      shared_subscription_id: '859a785c-bd38-402d-b595-1f44f40fb9bf'
    secrets:
      SHARED_CLIENT_ID: ${{ secrets.SHARED_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

  # ── JOB 3: Upload RAG Documents to Blob Storage (Phase 2 - Parallel) ───────
  upload-documents:
    name: Upload RAG Documents
    needs: devsecops-scan
    uses: RepoCodeGanesh/.github/.github/workflows/app-sync-docs.yml@main
    with:
      storage_account_name: 'sthttaxbpcin01'
      container_name: 'documents'
      source_directory: 'app/tax-advisor/documents'
      app_subscription_id: 'f4ffefe1-d689-4059-969c-ccc73e2a11d4'
    secrets:
      APP_CLIENT_ID: ${{ secrets.APP_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

  # ── JOB 4: Configure CORS Origins (Phase 3 - Waits for Frontend & Backend) ─
  configure-cors:
    name: Configure CORS & APIM
    needs: [deploy-backend, deploy-frontend]
    uses: RepoCodeGanesh/.github/.github/workflows/app-config-cors.yml@main
    with:
      static_web_app_name: 'stapp-ht-taxb-p-cin-01'
      function_app_name: 'func-ht-taxb-p-cin-01'
      resource_group: 'rg-ht-taxb-p-cin-01'
      app_subscription_id: 'f4ffefe1-d689-4059-969c-ccc73e2a11d4'
    secrets:
      APP_CLIENT_ID: ${{ secrets.APP_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

  # ── JOB 5: Enterprise SemVer Tagging & Release (Phase 4 - Final) ───────────
  create-release:
    name: Enterprise SemVer Release
    needs: [configure-cors, upload-documents]
    uses: RepoCodeGanesh/.github/.github/workflows/app-tag-semver.yml@main
    with:
      artifact_name: 'taxbot-backend-package'
      release_artifacts: 'functionapp.zip'
```

---

## 📊 Summary of Parallelization Benefits

1. **~50% Execution Time Reduction:** Backend Function App deploy, Frontend Static Web App deploy, and RAG document sync run simultaneously instead of waiting for each other sequentially.
2. **Deterministic Dependency Resolution:** CORS configuration (`configure-cors`) waits explicitly for both `deploy-backend` and `deploy-frontend` to complete before querying SWA endpoints.
