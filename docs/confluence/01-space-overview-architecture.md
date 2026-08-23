# 🏛️ HappyTechies Azure AI Landing Zone & Enterprise Copilots Overview

* **Space:** `HappyTechies Cloud & AI Platform`
* **Target Audience:** Cloud Platform Engineers, FinTech Architects, Security Auditors, DevOps
* **Owner:** `ai-platform-team@happytechies.com`
* **Status:** `ACTIVE / PRODUCTION`

---

## 🎯 1. Executive Summary

The **HappyTechies Azure AI Landing Zone** is an enterprise-grade, multi-subscription cloud platform designed according to the **Microsoft Cloud Adoption Framework (CAF)**. It hosts two production AI workloads with complete private network isolation, federated Workload Identity (OIDC), DevSecOps pipelines, and centralized observability, while maintaining a **near-zero idle running cost (~$0.15 to $0.30/month)**.

```
                   ┌─────────────────────────────────────────┐
                   │    Dual CI/CD (GitHub Actions & ADO)    │
                   └────────────────────┬────────────────────┘
                                        │ (Workload Identity Federation - OIDC)
                                        ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                         Azure Enterprise Subscriptions                    │
  ├───────────────────┬───────────────────┬───────────────────┬───────────────┤
  │     Bootstrap     │     Hub-prod      │  Shared-services  │   Apps-prod   │
  │   7689ad81-...    │   3eb8cc01-...    │   859a785c-...    │  f4ffefe1-... │
  ├───────────────────┼───────────────────┼───────────────────┼───────────────┤
  │ • Remote State    │ • Hub VNet        │ • Central Log     │ • TaxBot VNet │
  │   (sthtbootpcin01)│   (10.0.0.0/16)   │   Analytics       │   (10.41.0/16)│
  │ • Bootstrap KV    │ • Azure Firewall  │ • APIM Gateway    │ • BankC VNet  │
  │                   │   & Bastion       │ • Shared Key Vault│   (10.42.0/16)│
  │                   │   Subnets         │ • Shared Plan     │ • AKS Cluster │
  └───────────────────┴───────────────────┴───────────────────┴───────────────┘
```

---

## 🔑 2. Enterprise Subscriptions & Federated Identity Matrix

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

| Scope / Tier | Azure Subscription Name | Subscription ID | CI/CD Connection | Home Resources |
| :--- | :--- | :--- | :--- | :--- |
| **Bootstrap** | `bootstrap` | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` / `BOOTSTRAP_CLIENT_ID` | Terraform remote `.tfstate` backend storage (`sthtbootpcin01`) |
| **Hub Network** | `Hub-prod` | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` / `HUB_CLIENT_ID` | Central Hub VNet (`vnet-ht-hub-p-cin-01`) & central routing |
| **Shared Services** | `Shared-services` | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` / `SHARED_CLIENT_ID` | Central Log Analytics (`law-ht-ss-p-cin-01`), APIM Gateway (`Consumption_0`) |
| **AI Workloads** | `Apps-prod` | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` / `APP_CLIENT_ID` | TaxBot India (`10.41.0.0/16`) & BankCompliance AI AKS (`10.42.0.0/16`) |

---

## 🌐 3. Hub-and-Spoke Network Topology & Peering Matrix

```text
                               ┌─────────────────────────────────────────┐
                               │  CENTRAL HUB NETWORK (10.0.0.0/16)      │
                               │  vnet-ht-hub-p-cin-01 (Hub-prod)        │
                               │  • AzureFirewallSubnet: 10.0.1.0/26     │
                               │  • AzureBastionSubnet:  10.0.2.0/26     │
                               │  • GatewaySubnet:       10.0.3.0/27     │
                               └────────────────────┬────────────────────┘
                                                    │
                   ┌────────────────────────────────┼────────────────────────────────┐
                   │ (Two-Way VNet Peering)         │ (Two-Way VNet Peering)         │ (Two-Way VNet Peering)
                   ▼                                ▼                                ▼
┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐
│ SPOKE 1: TAXBOT PAAS (10.41.0.0/16)  │ │ SPOKE 2: BANKCOMPLIANCE (10.42.0.0/16)│ │ SHARED SERVICES VNET (10.43.0.0/16)  │
│ vnet-ht-taxb-p-cin-01 (Apps-prod)    │ │ vnet-ht-bankc-p-cin-01 (Apps-prod)   │ │ vnet-ht-ss-p-cin-01 (Shared-svcs)    │
│ • snet-taxb-app: 10.41.1.0/24        │ │ • snet-bankc-aks-nodes: 10.42.1.0/24 │ │ • snet-apim: 10.43.1.0/24            │
│ • snet-taxb-pe:  10.41.2.0/24        │ │ • snet-bankc-pe:        10.42.2.0/24 │ │ • snet-law:  10.43.2.0/24            │
│ • Private Link: Cosmos DB, AI Search │ │ • Pod Overlay CIDR:   192.168.0.0/16 │ │ • APIM Gateway (apim-ht-ss-p-cin-01) │
└──────────────────────────────────────┘ └──────────────────────────────────────┘ └──────────────────────────────────────┘
```

* **Hub Network (`10.0.0.0/16`)**:
  * `AzureFirewallSubnet`: `10.0.1.0/26` (Azure Firewall Premium/Standard)
  * `AzureBastionSubnet`: `10.0.2.0/26` (Azure Bastion Host for secure RDP/SSH)
  * `GatewaySubnet`: `10.0.3.0/27` (VPN / ExpressRoute Gateway)
* **Spoke 1 - TaxBot India (`10.41.0.0/16`)**:
  * `snet-taxb-app`: `10.41.1.0/24` (Function App VNet Integration)
  * `snet-taxb-pe`: `10.41.2.0/24` (Private Link for AI Search, OpenAI & Cosmos DB)
* **Spoke 2 - BankCompliance AI (`10.42.0.0/16`)**:
  * `snet-bankc-aks-nodes`: `10.42.1.0/24` (AKS Node Pool NICs on `Standard_B4ms`)
  * `snet-bankc-pe`: `10.42.2.0/24` (Private Endpoints for Key Vault & Storage)
  * `Pod Overlay CIDR`: `192.168.0.0/16` (Azure CNI Overlay — preserves private VNet IPs)

---

## 🚀 4. Active AI Workload Portfolio

| Workload | Live Production Domain | Primary Tech Stack | Architectural Paradigm |
| :--- | :--- | :--- | :--- |
| **TaxBot India** | **`https://www.mytaxbot.site`** | Python Function App, Azure AI Search, Azure OpenAI `gpt-5.4-nano`, Cosmos DB, React SPA | **Serverless PaaS** |
| **BankCompliance AI** | **`https://bank.mytaxbot.site`** | Azure Kubernetes Service (AKS Free Tier), LiteLLM Gateway, Qdrant Vector DB on 4GB CSI, React SPA | **Cloud-Native Kubernetes** |

---

## 🔒 5. Multi-Root Terraform Architecture
Each tier maintains its own state file in the remote backend `sthtbootpcin01` to enforce separation of blast radius:
* `platform/bootstrap` $\rightarrow$ `sthtbootpcin01/tfstate/bootstrap/prod.tfstate`
* `platform/hub` $\rightarrow$ `sthtbootpcin01/tfstate/hub/prod.tfstate`
* `platform/shared-services` $\rightarrow$ `sthtbootpcin01/tfstate/shared-services/prod.tfstate`
* `workloads/tax-advisor` $\rightarrow$ `sthtbootpcin01/tfstate/workloads/tax-advisor/prod.tfstate`
* `workloads/bank-compliance-ai-aks` $\rightarrow$ `sthtbootpcin01/tfstate/workloads/bank-compliance-ai-aks/prod.tfstate`
