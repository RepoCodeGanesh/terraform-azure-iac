# TaxBot India — Application CI/CD Pipeline & Architecture Flow

This document details the **CI/CD Pipeline Execution Flow** and **Runtime Traffic Architecture** for the TaxBot India (`workloads/tax-advisor`) workload.

> **Pipeline Definition File**: [`pipelines/azure-cicd-app-tax-advisor.yml`](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/pipelines/azure-cicd-app-tax-advisor.yml)  
> **Target Subscription**: `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`) via `app-prod` Service Connection (WIF OIDC)

---

## 1. CI/CD Pipeline Execution Flow

```mermaid
flowchart TD
    %% Trigger & Identity
    subgraph Trigger["1. Trigger & Authentication"]
        A["Git Push / PR on main or develop<br/>(app/tax-advisor/**)"] --> B["Workload Identity Federation (WIF)<br/>Service Connection: app-prod"]
    end

    %% Stage 0: DevSecOps Scan
    subgraph Stage0["Stage 0: DevSecOps SAST & SCA Scan"]
        B --> C1["Python SAST Scan<br/>(Bandit -ll -ii)"]
        B --> C2["Python SCA Vulnerability Scan<br/>(pip-audit requirements.txt)"]
        B --> C3["Frontend Dependency Audit<br/>(npm audit --audit-level=high)"]
        B --> C4["Enterprise SAST & Quality Gate<br/>(SonarCloud Analysis)"]
    end

    %% Stage 1: Deploy Backend
    subgraph Stage1["Stage 1: Package & Deploy Python Backend"]
        C1 & C2 & C3 & C4 --> D1["Install Linux-compatible Wheels<br/>(.python_packages manylinux2014)"]
        D1 --> D2["Archive Backend Code<br/>(functionapp.zip)"]
        D2 --> D3["Deploy via ZipDeploy<br/>Azure Function App: func-ht-taxb-p-cin-01"]
    end

    %% Stage 2: Upload Documents
    subgraph Stage2["Stage 2: RAG Knowledge Base Sync"]
        D3 --> E1["Read Statutory Tax Documents<br/>(app/tax-advisor/documents/*.txt)"]
        E1 --> E2["az storage blob upload-batch<br/>(Entra ID RBAC login)"]
        E2 --> E3["Upload to Blob Container: documents<br/>Storage Account: sthttaxbpcin01"]
    end

    %% Stage 3: Deploy Frontend
    subgraph Stage3["Stage 3: Build & Deploy React Frontend"]
        E3 --> F1["Fetch SWA Token from Key Vault<br/>kv-ht-ss-p-cin-01 (Shared Services)"]
        F1 --> F2["Build Production React SPA<br/>(npm run build -> dist)"]
        F2 --> F3["Deploy static bundle<br/>Azure Static Web App: stapp-ht-taxb-p-cin-01"]
    end

    %% Stage 4: CORS & Security
    subgraph Stage4["Stage 4: CORS & Security Lockdown"]
        F3 --> G1["Query SWA Default Hostname<br/>(az staticwebapp show)"]
        G1 --> G2["Configure Function App CORS<br/>(az functionapp cors add)"]
        G2 --> G3["Final Status: Deployed & Live<br/>www.mytaxbot.site"]
    end

    %% Styling
    classDef trigger fill:#1f2937,stroke:#60a5fa,color:#fff;
    classDef stage0 fill:#111827,stroke:#f59e0b,color:#fff;
    classDef stage1 fill:#111827,stroke:#10b981,color:#fff;
    classDef stage2 fill:#111827,stroke:#06b6d4,color:#fff;
    classDef stage3 fill:#111827,stroke:#8b5cf6,color:#fff;
    classDef stage4 fill:#111827,stroke:#ec4899,color:#fff;

    class A,B trigger;
    class C1,C2,C3,C4 stage0;
    class D1,D2,D3 stage1;
    class E1,E2,E3 stage2;
    class F1,F2,F3 stage3;
    class G1,G2,G3 stage4;
```

---

## 2. Live Runtime Sequence Architecture

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

## 3. Stage & Task Breakdown

| Stage ID | Stage Name | Operational Tasks & Scans | Target Azure Resource |
| :--- | :--- | :--- | :--- |
| **Stage 0** | **DevSecOps Security Scan** | `Bandit` (Python SAST), `pip-audit` (SCA), `npm audit` (Frontend), `SonarCloud` Analysis | Build Agent / SonarCloud |
| **Stage 1** | **Deploy Backend** | Python 3.11 wheel packaging (`manylinux2014_x86_64`), `ZipDeploy` | Function App `func-ht-taxb-p-cin-01` |
| **Stage 2** | **Upload RAG Docs** | Entra ID RBAC login (`--auth-mode login`), batch upload 15 FY 2026-27 text files | Storage Account `sthttaxbpcin01/documents` |
| **Stage 3** | **Deploy Frontend** | Fetch token from Key Vault `kv-ht-ss-p-cin-01`, Vite React build (`npm run build`), SWA deploy | Static Web App `stapp-ht-taxb-p-cin-01` |
| **Stage 4** | **CORS & Security** | Resolve SWA hostname, update allowed origins on Function App | Azure Function App CORS config |
