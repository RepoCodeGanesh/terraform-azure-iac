# Platform Guide 01 — Azure AI Landing Zone Overview

[← Back to Master Index](file:///c:/Users/RichT/OneDrive/Documents/Repos/migrate/terraform-azure-iac/docs/platform-guide/README.md)

---

## 🎯 Executive Overview

The **Azure AI Landing Zone** is an enterprise-grade, multi-subscription cloud platform built following the **Microsoft Cloud Adoption Framework (CAF)** Enterprise-Scale Landing Zone pattern. 

Provisioned using **Terraform Infrastructure as Code (IaC)** and **Dual CI/CD Pipelines (Azure DevOps & GitHub Actions)**, the platform hosts high-performance AI workloads—such as **TaxBot India (AI Income Tax Advisor)**—while maintaining near-zero idle running costs ($0–$15/month).

---

## 🏛️ Subscription Topology & Identity Mapping

The architecture segregates responsibilities across four distinct Azure subscriptions. Each subscription uses **Workload Identity Federation (WIF / OIDC)** via Entra ID App Registrations without hardcoded secrets.

```mermaid
flowchart LR
    subgraph Bootstrap ["Bootstrap Subscription"]
        direction TB
        B_ID["ID: 7689ad81-71ba-481b-a17c-e1b6be61bab1"]
        B_SC["ADO Service Connection: bootstrap"]
        B_RES["sthtbootpcin01 (State Storage)<br>kv-ht-boot-p-cin-01 (Secrets)"]
    end

    subgraph Hub ["Hub-prod Subscription"]
        direction TB
        H_ID["ID: 3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b"]
        H_SC["ADO Service Connection: hub-prod"]
        H_RES["vnet-ht-hub-p-cin-01 (Hub VNet)<br>AzureFirewallSubnet & Bastion"]
    end

    subgraph Shared ["Shared-services Subscription"]
        direction TB
        S_ID["ID: 859a785c-bd38-402d-b595-1f44f40fb9bf"]
        S_SC["ADO Service Connection: shared-services"]
        S_RES["law-ht-ss-p-cin-01 (Log Analytics)<br>apim-ht-ss-p-cin-01 (Consumption)<br>kv-ht-ss-p-cin-01 (Shared KV)"]
    end

    subgraph Apps ["Apps-prod Subscription"]
        direction TB
        A_ID["ID: f4ffefe1-d689-4059-969c-ccc73e2a11d4"]
        A_SC["ADO Service Connection: app-prod"]
        A_RES["rg-ht-taxb-p-cin-01 (TaxBot RG)<br>oai-ht-taxb-p-eus-01 (OpenAI)<br>srch-ht-taxb-p-cin-01 (AI Search)<br>func-ht-taxb-p-cin-01 (Function)<br>stapp-ht-taxb-p-cin-01 (SWA UI)"]
    end
```

### Subscription Summary Table

| Subscription Name | Azure Subscription ID | ADO Service Connection | Entra ID App Registration Client ID | Primary Role |
| :--- | :--- | :--- | :--- | :--- |
| **bootstrap** | `7689ad81-71ba-481b-a17c-e1b6be61bab1` | `bootstrap` | `934ab83b-2f61-475e-bdbc-85c9eaed83e6` | Remote Terraform `.tfstate` storage backend & bootstrap Key Vault |
| **Hub-prod** | `3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b` | `hub-prod` | `78960c14-26d2-4a0c-ab21-579c3030155e` | Central Hub VNet, routing, firewall, bastion management |
| **Shared-services** | `859a785c-bd38-402d-b595-1f44f40fb9bf` | `shared-services` | `580ffcfd-51ee-4dc3-9204-d03cb438ff82` | Log Analytics workspace, APIM gateway, Shared Key Vault |
| **Apps-prod** | `f4ffefe1-d689-4059-969c-ccc73e2a11d4` | `app-prod` | `99ab7987-3989-46c3-bae9-92279be16608` | AI Workloads — TaxBot India (`workloads/tax-advisor` & `app/tax-advisor`) |

---

## 🌐 Hub-and-Spoke Network Architecture

The network layout enforces strict micro-segmentation with bi-directional VNet peering between the Hub and Workload Spokes.

```mermaid
graph TD
    subgraph HubVNet ["Hub Network (vnet-ht-hub-p-cin-01) — 10.0.0.0/16"]
        FW["AzureFirewallSubnet<br>10.0.0.0/26"]
        BAS["AzureBastionSubnet<br>10.0.0.64/27"]
        GW["GatewaySubnet<br>10.0.0.96/27"]
    end

    subgraph SpokeVNet ["TaxBot Spoke Network (vnet-ht-taxb-p-cin-01) — 10.41.0.0/16"]
        SNET_APP["snet-app-integration<br>10.41.1.0/24<br><i>(Function App VNet Integration)</i>"]
        SNET_PE["PrivateEndpoints<br>10.41.2.0/24<br><i>(Private Link: OpenAI, Storage, Search)</i>"]
    end

    HubVNet <== "Bi-Directional VNet Peering<br>(module.taxb_to_hub_peering)" ==> SpokeVNet
```

### Network Subnet Reference

| VNet Name | CIDR Range | Subnet Name | Subnet CIDR | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `vnet-ht-hub-p-cin-01` | `10.0.0.0/16` | `AzureFirewallSubnet` | `10.0.0.0/26` | Central ingress/egress firewall inspection |
| | | `AzureBastionSubnet` | `10.0.0.64/27` | Secure management jumpbox access |
| | | `GatewaySubnet` | `10.0.0.96/27` | ExpressRoute / S2S VPN gateway |
| `vnet-ht-taxb-p-cin-01` | `10.41.0.0/16` | `snet-app-integration` | `10.41.1.0/24` | Swift VNet Integration for Python Function App |
| | | `PrivateEndpoints` | `10.41.2.0/24` | Private Endpoints for OpenAI, Storage, Search & Cosmos DB |

---

## 🔒 Multi-Root Terraform State Isolation

> [!IMPORTANT]
> **State Isolation Rule**: Never merge Terraform state files into a single root. Each layer (`platform/bootstrap`, `platform/hub`, `platform/shared-services`, and `workloads/tax-advisor`) runs as an independent Terraform root with its own isolated `.tfstate` file stored in `sthtbootpcin01`.

```mermaid
flowchart TD
    subgraph StorageAccount ["Backend Storage: sthtbootpcin01 (bootstrap sub)"]
        BLOB1["tfstate/bootstrap/prod.tfstate"]
        BLOB2["tfstate/hub/prod.tfstate"]
        BLOB3["tfstate/shared-services/prod.tfstate"]
        BLOB4["tfstate/workloads/tax-advisor/prod.tfstate"]
    end

    ROOT1["platform/bootstrap"] --> BLOB1
    ROOT2["platform/hub"] --> BLOB2
    ROOT3["platform/shared-services"] --> BLOB3
    ROOT4["workloads/tax-advisor"] --> BLOB4
```

---

## 🚀 Strict Platform Deployment Sequence

Deploy platform roots in strict order to satisfy inter-layer dependencies:

```mermaid
flowchart TD
    S1["1. platform/bootstrap<br><i>(State Storage & Key Vault)</i>"] --> S2["2. platform/hub<br><i>(Hub VNet & Subnets)</i>"]
    S2 --> S3["3. platform/shared-services<br><i>(APIM, Log Analytics & Shared Key Vault)</i>"]
    S3 --> S4["4. workloads/tax-advisor<br><i>(Spoke VNet, Peering, AI Resources, Function App Host)</i>"]
    S4 --> S5["5. app/tax-advisor<br><i>(Python ZipDeploy + RAG Blob Sync + React SPA UI)</i>"]
```
