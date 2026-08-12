# Platform Guide 03 — Dual CI/CD Pipelines & WIF Authentication

[← Back to Master Index](README.md)

---

## ⚡ Overview & Dual Engine Strategy

This repository supports **Dual CI/CD Automation**:
1. **Azure DevOps Pipelines (`pipelines/*.yml`)**: Enterprise-grade YAML pipelines with manual approvals and environments.
2. **GitHub Actions Workflows (`.github/workflows/*.yml`)**: Reusable workflow templates powered by OIDC authentication.

Both engines enforce **Workload Identity Federation (WIF / OIDC)**—eliminating all stored secret keys or service principal passwords.

---

## 🔑 Workload Identity Federation (OIDC) Matrix

```mermaid
flowchart LR
    subgraph Identities ["Entra ID App Registrations"]
        APP_BOOT["DevOpsUniverse-Terraform-bootstrap<br><code>934ab83b-2f61-475e-bdbc-85c9eaed83e6</code>"]
        APP_HUB["DevOpsUniverse-Terraform-hub-prod<br><code>78960c14-26d2-4a0c-ab21-579c3030155e</code>"]
        APP_SS["DevOpsUniverse-Terraform-shared-services<br><code>580ffcfd-51ee-4dc3-9204-d03cb438ff82</code>"]
        APP_APP["DevOpsUniverse-Terraform-app-prod<br><code>99ab7987-3989-46c3-bae9-92279be16608</code>"]
    end

    subgraph ADO ["Azure DevOps Pipelines"]
        ADO_BOOT["azure-cicd-bootstrap.yml<br>(sc: bootstrap)"]
        ADO_HUB["azure-cicd-hub.yml<br>(sc: hub-prod)"]
        ADO_SS["azure-cicd-shared-ser.yml<br>(sc: shared-services)"]
        ADO_APP["azure-cicd-app-tax-advisor.yml<br>(sc: app-prod)"]
    end

    subgraph GHA ["GitHub Actions Workflows"]
        GHA_BOOT["platform-bootstrap.yml<br>(secret: BOOTSTRAP_CLIENT_ID)"]
        GHA_HUB["platform-hub.yml<br>(secret: HUB_CLIENT_ID)"]
        GHA_SS["platform-shared-services.yml<br>(secret: SHARED_CLIENT_ID)"]
        GHA_APP["app-tax-advisor.yml<br>(secret: APP_CLIENT_ID)"]
    end

    APP_BOOT <--> ADO_BOOT & GHA_BOOT
    APP_HUB <--> ADO_HUB & GHA_HUB
    APP_SS <--> ADO_SS & GHA_SS
    APP_APP <--> ADO_APP & GHA_APP
```

---

## 🛠️ Infrastructure IaC Pipeline Stages (3-Stage Lifecycle)

All Terraform IaC pipelines (`bootstrap`, `hub`, `shared-services`, `tax-advisor`) execute through a strict 3-stage governance lifecycle:

```mermaid
flowchart TD
    subgraph Stage1 ["Stage 1: Validate"]
        INIT["terraform init -backend-config=backend.hcl"] --> FMT["terraform fmt -check -recursive"]
        FMT --> VAL["terraform validate"]
    end

    subgraph Stage2 ["Stage 2: Plan (PRs & Merges)"]
        PLAN["terraform plan -var-file=prod.tfvars -out=tfplan"] --> ART["Publish Speculative Plan Artifact"]
    end

    subgraph Stage3 ["Stage 3: Apply (Main/Develop Only)"]
        GATE["Environment Approval Gate (production)"] --> APPLY["terraform apply tfplan"]
    end

    Stage1 --> Stage2 --> Stage3
```

---

## 🚀 Application CI/CD Pipeline Stages (`app-tax-advisor.yml`)

The application deployment workflow executes across 5 sequential job stages:

```mermaid
flowchart TD
    J0["Job 0: DevSecOps SAST & SCA Scan<br><i>(Bandit, pip-audit, SonarCloud)</i>"]
    J1["Job 1: Package & Deploy Python Backend<br><i>(ZipDeploy functionapp.zip to func-ht-taxb-p-cin-01)</i>"]
    J2["Job 2: Upload RAG Text Files<br><i>(Sync 10 statutory docs to sthttaxbpcin01/documents)</i>"]
    J3["Job 3: Build & Deploy React UI<br><i>(Vite build -> Azure Static Web App stapp-ht-taxb-p-cin-01)</i>"]
    J4["Job 4: Configure CORS & Enterprise SemVer<br><i>(Set SWA CORS origin + Attach functionapp.zip to GitHub Release)</i>"]

    J0 --> J1 --> J2 --> J3 --> J4
```

### Application Job Summary Table

| Job ID | Job Name | Action & Security Controls | Target Resource |
| :---: | :--- | :--- | :--- |
| **Job 0** | DevSecOps SAST/SCA Scan | Runs `Bandit` (Python SAST), `pip-audit` (SCA vulnerabilities), `npm audit`, and `SonarCloud`. | Source Code Repository |
| **Job 1** | Deploy Python Backend | Installs `manylinux2014` wheels into `.python_packages`, archives `functionapp.zip`, uploads build artifact, and executes ZipDeploy with healthcheck. | `func-ht-taxb-p-cin-01` |
| **Job 2** | Upload RAG Documents | Syncs 10 statutory tax files from `app/tax-advisor/documents/` using Entra ID RBAC. | `sthttaxbpcin01/documents` |
| **Job 3** | Build & Deploy React UI | Fetches deployment token from Key Vault (`kv-ht-ss-p-cin-01`), runs `npm run build`, and deploys to Static Web App. | `stapp-ht-taxb-p-cin-01` |
| **Job 4** | CORS & SemVer Release | Queries SWA default hostname, configures Function App CORS allowed origins, tags commit (`vX.Y.Z`), and publishes GitHub Release with attached `functionapp.zip`. | Function App & GitHub Releases |

---

## 🌐 Live Runtime Sequence Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser / Client
    participant Domain as www.mytaxbot.site
    participant SWA as Azure Static Web App<br/>(stapp-ht-taxb-p-cin-01)
    participant APIM as APIM Gateway<br/>(apim-ht-ss-p-cin-01)
    participant Func as Azure Function App<br/>(func-ht-taxb-p-cin-01)
    participant Search as Azure AI Search<br/>(srch-ht-taxb-p-cin-01)
    participant OAI as Azure OpenAI<br/>(gpt-5.4-nano)
    participant DB as Azure Cosmos DB<br/>(cosmos-ht-taxb-p-cin-01)

    User->>Domain: 1. Request Web Page
    Domain->>SWA: 2. Serve React SPA Assets
    User->>APIM: 3. POST /api/chat (Rate Limited: 20 req/min)
    APIM->>Func: 4. Forward Authorized Request (CORS Validated)
    Func->>Search: 5. Retrieve Statutory RAG Tax Context (FY 2026-27)
    Search-->>Func: 6. Return Relevant Legal Tax Clauses
    Func->>OAI: 7. Prompt with Context & User Query
    OAI-->>Func: 8. Return Tax Calculation & Recommendation
    Func->>DB: 9. Persist Session & Conversation State
    Func-->>APIM: 10. HTTP 200 OK (Tax Response JSON)
    APIM-->>User: 11. Render Answer in React UI
```

---

## 🏷️ Automated SemVer & Release Asset Attachment

When a push occurs on `main` or a `release/*` branch, the pipeline automatically:
1. Calculates the next Semantic Version tag (`v1.0.X` for fixes, `v1.1.X` for features).
2. Pushes the Git tag (`v1.2.0`).
3. Downloads `functionapp.zip` build artifact and attaches it to the official GitHub Release assets tab.

```yaml
- name: Create Official GitHub Release with Attached Build Artifacts
  uses: ncipollo/release-action@v1
  with:
    tag: ${{ steps.tag_version.outputs.new_tag }}
    name: Release ${{ steps.tag_version.outputs.new_tag }}
    body: ${{ steps.tag_version.outputs.changelog }}
    artifacts: "functionapp.zip"
    token: ${{ secrets.GITHUB_TOKEN }}
```
