# Azure AI Landing Zone — Platform Guide Documentation

Welcome to the **Platform Guide Documentation Suite** for the enterprise-grade **Azure AI Landing Zone** and **TaxBot India** AI workload platform.

This suite provides interactive diagrams, architectural specs, deployment blueprints, troubleshooting playbooks, and operational standards following the **Microsoft Cloud Adoption Framework (CAF)**.

---

## 🗺️ Master Platform Architecture

```mermaid
flowchart TD
    subgraph DevOps ["CI/CD Pipelines (Dual Engine)"]
        ADO["Azure DevOps Pipelines<br><code>pipelines/azure-cicd-*.yml</code>"]
        GHA["GitHub Actions Workflows<br><code>.github/workflows/*.yml</code>"]
    end

    subgraph Subscriptions ["Azure Subscription Hierarchy (Workload Identity Federation)"]
        subgraph Sub_Boot ["1. Bootstrap Subscription"]
            ST_BOOT["sthtbootpcin01<br>(Remote TF State)"]
            KV_BOOT["kv-ht-boot-p-cin-01<br>(Boot Secrets)"]
        end

        subgraph Sub_Hub ["2. Hub-prod Subscription"]
            VNET_HUB["vnet-ht-hub-p-cin-01<br>(10.0.0.0/16)"]
            FW_SUB["AzureFirewallSubnet<br>(10.0.0.0/26)"]
            BAS_SUB["AzureBastionSubnet<br>(10.0.0.64/27)"]
        end

        subgraph Sub_SS ["3. Shared-services Subscription"]
            LAW["law-ht-ss-p-cin-01<br>(Log Analytics)"]
            APIM["apim-ht-ss-p-cin-01<br>(Consumption Gateway)"]
            KV_SS["kv-ht-ss-p-cin-01<br>(Shared Key Vault)"]
        end

        subgraph Sub_Apps ["4. Apps-prod Subscription"]
            VNET_SPOKE["vnet-ht-taxb-p-cin-01<br>(10.41.0.0/16)"]
            OAI["oai-ht-taxb-p-eus-01<br>(gpt-5.4-nano)"]
            SRCH["srch-ht-taxb-p-cin-01<br>(AI Search RAG)"]
            COSMOS["cosmos-ht-taxb-p-cin-01<br>(Serverless State)"]
            FUNC["func-ht-taxb-p-cin-01<br>(Python Backend)"]
            SWA["stapp-ht-taxb-p-cin-01<br>(www.mytaxbot.site)"]
        end
    end

    DevOps -->|"WIF (OIDC)"| Subscriptions
    VNET_HUB <== "Bi-Directional VNet Peering" ==> VNET_SPOKE
    APIM -->|"Secure Proxy & Rate Limit"| FUNC
    SWA -->|"React SPA UI"| APIM
    FUNC --> OAI & SRCH & COSMOS
    Sub_Apps -.->|"Diagnostics & Telemetry"| LAW
```

---

## 📚 Platform Guides Index

Click any guide below for detailed specs, operational runbooks, and deep-dive technical guides:

| Module | Guide Title | Core Topics & Visuals | Link |
| :---: | :--- | :--- | :---: |
| **01** | **Platform Overview** | Subscription topology, Hub-Spoke networks, deployment order. | [01-platform-overview.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/01-platform-overview.md) |
| **02** | **Terraform IaC Guide** | Roots vs modules, state rules, layer dependencies. | [02-terraform-iac-guide.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/02-terraform-iac-guide.md) |
| **03** | **CI/CD Pipelines Guide** | Dual CI/CD authentication, 3-Stage IaC & 4-Stage App workflows. | [03-cicd-pipelines-guide.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/03-cicd-pipelines-guide.md) |
| **04** | **Naming & Standards** | CAF resource naming syntax, 12 resource type examples, mandatory tags. | [04-naming-and-standards.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/04-naming-and-standards.md) |
| **05** | **Troubleshooting Guide** | Incident flowchart, APIM 500, SWA CORS, Tax rules (80CCD(2), Rule 2A HRA). | [05-troubleshooting-guide.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/05-troubleshooting-guide.md) |
| **06** | **Blue-Green Deployments** | Zero-downtime slot swaps, SWA global CDN cutover, 1-click rollback. | [06-blue-green-deployment-guide.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/06-blue-green-deployment-guide.md) |
| **07** | **Monitoring & Telemetry** | Log Analytics aggregation, Application Insights, KQL queries, alerts. | [07-monitoring-telemetry-guide.md](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/07-monitoring-telemetry-guide.md) |

---

## ⚡ Deployment Quick Reference

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Developer / Pipeline
    participant Boot as 1. Bootstrap
    participant Hub as 2. Hub Network
    participant SS as 3. Shared Services
    participant Taxb as 4. TaxBot IaC
    participant App as 5. TaxBot App

    Dev->>Boot: terraform apply (platform/bootstrap)
    Note over Boot: Provisions State Storage Account & Key Vault
    Dev->>Hub: terraform apply (platform/hub)
    Note over Hub: Provisions Hub VNet (10.0.0.0/16)
    Dev->>SS: terraform apply (platform/shared-services)
    Note over SS: Provisions APIM, Log Analytics & Shared Key Vault
    Dev->>Taxb: terraform apply (workloads/tax-advisor)
    Note over Taxb: Provisions Spoke VNet, OpenAI, AI Search, Cosmos, Function
    Dev->>App: CI/CD Pipeline (app/tax-advisor)
    Note over App: Deploys Python ZipDeploy + RAG Blob Sync + React SPA
```
