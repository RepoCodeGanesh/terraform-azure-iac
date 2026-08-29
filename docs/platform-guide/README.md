# Azure AI Landing Zone — Platform Guide Documentation

[← Back to Master Documentation Hub](../README.md)

Welcome to the **Platform Guide Documentation Suite** for the enterprise-grade **Azure AI Landing Zone**, hosting **TaxBot India** (Serverless PaaS) and **BankCompliance AI** (Cloud-Native AKS).

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
        subgraph Sub_Boot ["1. Bootstrap Subscription (7689ad81)"]
            ST_BOOT["sthtbootpcin01<br>(Remote TF State)"]
            KV_BOOT["kv-ht-boot-p-cin-01<br>(Boot Secrets)"]
        end

        subgraph Sub_Hub ["2. Hub-prod Subscription (3eb8cc01)"]
            VNET_HUB["vnet-ht-hub-p-cin-01<br>(10.0.0.0/16)"]
            FW_SUB["AzureFirewallSubnet<br>(10.0.0.0/26)"]
            BAS_SUB["AzureBastionSubnet<br>(10.0.0.64/27)"]
        end

        subgraph Sub_SS ["3. Shared-services Subscription (859a785c)"]
            LAW["law-ht-ss-p-cin-01<br>(Log Analytics)"]
            APIM["apim-ht-ss-p-cin-01<br>(Consumption Gateway)"]
            KV_SS["kv-ht-ss-p-cin-01<br>(Shared Key Vault)"]
        end

        subgraph Sub_Apps ["4. Apps-prod Subscription (f4ffefe1)"]
            subgraph Spoke_Tax ["Spoke 1: TaxBot India (10.41.0.0/16)"]
                FUNC["func-ht-taxb-p-cin-01<br>(Python Backend)"]
                OAI["oai-ht-taxb-p-eus-01<br>(gpt-5.4-nano)"]
                SRCH["srch-ht-taxb-p-cin-01<br>(AI Search RAG)"]
                COSMOS["cosmos-ht-taxb-p-cin-01<br>(Serverless State)"]
                SWA_TAX["stapp-ht-taxb-p-cin-01<br>(www.mytaxbot.site)"]
            end

            subgraph Spoke_Bank ["Spoke 2: BankCompliance AI (10.42.0.0/16)"]
                AKS["aks-ht-bankc-p-cin-01<br>(Standard_B4ms Free Tier)"]
                QDRANT["Qdrant Vector DB<br>(4GB CSI Disk)"]
                LITELLM["LiteLLM AI Gateway<br>(Gemini + Azure DR)"]
                SWA_BANK["stapp-ht-bankc-p-cin-01<br>(bank.mytaxbot.site)"]
            end
        end
    end

    DevOps -->|"WIF (OIDC)"| Subscriptions
    VNET_HUB <== "Peering" ==> Spoke_Tax
    VNET_HUB <== "Peering" ==> Spoke_Bank
    SWA_TAX -->|"React SPA"| APIM -->|"Rate Limited Proxy"| FUNC
    SWA_BANK -->|"React SPA"| APIM -->|"SSL Offload"| AKS
    FUNC --> OAI & SRCH & COSMOS
    AKS --> QDRANT & LITELLM
    Sub_Apps -.->|"Diagnostics & Telemetry"| LAW
```

---

## 📚 Platform Guides Index

Click any guide below for detailed specs, operational runbooks, and deep-dive technical guides:

| Module | Guide Title | Core Topics & Visuals | Link |
| :---: | :--- | :--- | :---: |
| **01** | **Platform Overview** | Subscription topology, Hub-Spoke networks, deployment order. | [01-platform-overview.md](01-platform-overview.md) |
| **02** | **Terraform IaC Guide** | Roots vs modules, state rules, layer dependencies. | [02-terraform-iac-guide.md](02-terraform-iac-guide.md) |
| **03** | **CI/CD Pipelines Guide** | Dual CI/CD authentication, 3-Stage IaC & 4-Stage App workflows. | [03-cicd-pipelines-guide.md](03-cicd-pipelines-guide.md) |
| **04** | **Naming & Standards** | CAF resource naming syntax, 12 resource type examples, mandatory tags. | [04-naming-and-standards.md](04-naming-and-standards.md) |
| **05** | **Troubleshooting Guide** | Incident flowchart, APIM 500, SWA CORS, Tax rules (80CCD(2), Rule 2A HRA). | [05-troubleshooting-guide.md](05-troubleshooting-guide.md) |
| **06** | **Blue-Green Deployments** | Zero-downtime slot swaps, SWA global CDN cutover, 1-click rollback. | [06-blue-green-deployment-guide.md](06-blue-green-deployment-guide.md) |
| **07** | **Monitoring & Telemetry** | Log Analytics aggregation, Application Insights, KQL queries, alerts. | [07-monitoring-telemetry-guide.md](07-monitoring-telemetry-guide.md) |
| **08** | **Azure RAG Architectures** | Master RAG taxonomy, 6 architectures, adoption matrix, decision playbook. | [08-azure-rag-architectural-patterns.md](08-azure-rag-architectural-patterns.md) |
| **09** | **Multi-Cloud AI Gateway** | Active-Passive resilient gateway (Gemini Primary $0 + Azure OpenAI Fallback). | [09-multi-cloud-ai-gateway-and-fallback-guide.md](09-multi-cloud-ai-gateway-and-fallback-guide.md) |
| **10** | **AI Engineering Roadmap** | 4-Phase Roadmap & Gap Analysis (Core, Ingestion, Multi-Agent, Private Lockdown). | [10-enterprise-ai-engineering-backlog-and-roadmap.md](10-enterprise-ai-engineering-backlog-and-roadmap.md) |
| **11** | **GenAI Evaluation & Testing** | 6-Tier testing pyramid, Ragas triad, golden datasets, red teaming, FinOps token caps. | [11-enterprise-genai-evaluation-and-testing-framework.md](11-enterprise-genai-evaluation-and-testing-framework.md) |

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
    participant Bankc as 5. BankCompliance IaC
    participant Apps as 6. App Deployments

    Dev->>Boot: terraform apply (platform/bootstrap)
    Note over Boot: Provisions State Storage Account & Key Vault
    Dev->>Hub: terraform apply (platform/hub)
    Note over Hub: Provisions Hub VNet (10.0.0.0/16)
    Dev->>SS: terraform apply (platform/shared-services)
    Note over SS: Provisions APIM, Log Analytics & Shared Key Vault
    Dev->>Taxb: terraform apply (workloads/tax-advisor)
    Note over Taxb: Provisions Spoke VNet (10.41.0.0/16), OpenAI, AI Search, Cosmos, Function
    Dev->>Bankc: terraform apply (workloads/bank-compliance-ai-aks)
    Note over Bankc: Provisions Spoke VNet (10.42.0.0/16), AKS Free Tier & Content Safety
    Dev->>Apps: CI/CD Pipelines (app/tax-advisor & app/bank-compliance)
    Note over Apps: Deploys Functions, Helm Chart to AKS & React SPAs to SWA
```
