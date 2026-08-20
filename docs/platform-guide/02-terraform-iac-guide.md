# Platform Guide 02 — Terraform IaC & Module Architecture

[← Back to Master Index](README.md)

---

## 🏗️ Repository Directory Structure

The repository maintains strict separation between **Platform Layers** (independent deployment roots with dedicated state files) and **Reusable Modules** (subscription-agnostic building blocks).

```
terraform-azure-iac/
├── platform/                     ── Platform Infrastructure Layers (Independent Roots)
│   ├── bootstrap/                ── Layer 1: Storage Account & Key Vault for TF State
│   ├── hub/                      ── Layer 2: Hub VNet, Firewall & Bastion Subnets
│   └── shared-services/          ── Layer 3: APIM Gateway, Log Analytics & Key Vault
├── workloads/                    ── Application Workload IaC Layers
│   ├── tax-advisor/              ── Layer 4: TaxBot India (OpenAI, Search, Cosmos, Function)
│   └── bank-compliance-ai-aks/   ── Layer 5: BankCompliance AI (AKS, Content Safety, SWA)
├── modules/                      ── Reusable Subscription-Agnostic Modules
│   ├── naming/                   ── CAF Resource Naming Helper Module
│   ├── network/                  ── VNet & Subnet Wrapper Module
│   ├── aks/                      ── AKS Cluster & Node Pool Module
│   └── vnet_peering/             ── Cross-Subscription VNet Peering (Aliased Providers)
└── app/                          ── Application Codebase & Workloads
    ├── tax-advisor/              ── TaxBot India (React SPA + Python Azure Function)
    └── bank-compliance/          ── BankCompliance AI (React SPA + FastAPI + K8s Manifests)
```

---

## 🧩 Module Dependency Architecture

```mermaid
flowchart TD
    subgraph Modules ["Reusable Modules (modules/)"]
        M_NAME["modules/naming<br>(CAF Conventions)"]
        M_NET["modules/network<br>(VNet + Subnets)"]
        M_PEER["modules/vnet_peering<br>(Aliased Providers)"]
    end

    subgraph Roots ["Terraform Roots (platform/* & workloads/*)"]
        R_BOOT["platform/bootstrap"]
        R_HUB["platform/hub"]
        R_SS["platform/shared-services"]
        R_TAXB["workloads/tax-advisor"]
    end

    R_BOOT --> M_NAME
    R_HUB --> M_NAME & M_NET
    R_SS --> M_NAME
    R_TAXB --> M_NAME & M_NET & M_PEER
```

---

## 🔍 Layer Breakdown & Resource Provisioning

### 1. Layer 1: Bootstrap (`platform/bootstrap`)
* **Target Subscription**: `bootstrap` (`7689ad81-71ba-481b-a17c-e1b6be61bab1`)
* **Backend State Location**: Stored locally on first run, then migrated to `sthtbootpcin01/tfstate/bootstrap/prod.tfstate`
* **Provisioned Resources**:
  * `azurerm_resource_group`: `rg-ht-boot-p-cin-01`
  * `azurerm_storage_account`: `sthtbootpcin01` (`Standard_LRS`, TLS 1.2, Blob container: `tfstate`)
  * `azurerm_key_vault`: `kv-ht-boot-p-cin-01` (Standard SKU with Azure RBAC authorization model)

### 2. Layer 2: Hub Network (`platform/hub`)
* **Target Subscription**: `Hub-prod` (`3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b`)
* **Backend State Location**: `sthtbootpcin01/tfstate/hub/prod.tfstate`
* **Provisioned Resources**:
  * `azurerm_resource_group`: `rg-ht-hub-p-cin-01`
  * `module.hub_vnet`: `vnet-ht-hub-p-cin-01` (`10.0.0.0/16`) with `AzureFirewallSubnet`, `AzureBastionSubnet`, and `GatewaySubnet`

### 3. Layer 3: Shared Services (`platform/shared-services`)
* **Target Subscription**: `Shared-services` (`859a785c-bd38-402d-b595-1f44f40fb9bf`)
* **Backend State Location**: `sthtbootpcin01/tfstate/shared-services/prod.tfstate`
* **Provisioned Resources**:
  * `azurerm_resource_group`: `rg-ht-ss-p-cin-01`
  * `azurerm_log_analytics_workspace`: `law-ht-ss-p-cin-01` (`PerGB2018`, 30-day retention)
  * `azurerm_api_management`: `apim-ht-ss-p-cin-01` (`Consumption_0` SKU — $0 base cost)
  * `azurerm_key_vault`: `kv-ht-ss-p-cin-01` (Stores SWA deployment token)
  * `azurerm_service_plan`: `asp-ht-ss-p-cin-01` (Free `F1` tier host)

### 4. Layer 4: Workloads — TaxBot India (`workloads/tax-advisor`)
* **Target Subscription**: `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`)
* **Backend State Location**: `sthtbootpcin01/tfstate/workloads/tax-advisor/prod.tfstate`
* **Provisioned Resources**:
  * `azurerm_resource_group`: `rg-ht-taxb-p-cin-01`
  * `module.taxb_vnet`: `vnet-ht-taxb-p-cin-01` (`10.41.0.0/16`)
  * `module.taxb_to_hub_peering`: Bi-directional VNet peering to `vnet-ht-hub-p-cin-01` (via aliased `azurerm.hub` provider)
  * `module.openai`: `oai-ht-taxb-p-eus-01` (`S0` SKU with `gpt-5.4-nano` deployment)
  * `module.search_service`: `srch-ht-taxb-p-cin-01` (`Basic` SKU with semantic ranker)
  * `module.cosmos_db`: `cosmos-ht-taxb-p-cin-01` (`Serverless` SKU)
  * `module.function_app`: `func-ht-taxb-p-cin-01` (`Consumption Y1` SKU, Python 3.11)
  * `azurerm_static_web_app`: `stapp-ht-taxb-p-cin-01` (`Free` tier bound to custom domain **www.mytaxbot.site**)
  * `azapi_resource.apim_tax_advisor_api`: APIM API registration & rate-limiting policies

### 5. Layer 5: Workloads — BankCompliance AI AKS (`workloads/bank-compliance-ai-aks`)
* **Target Subscription**: `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`)
* **Backend State Location**: `sthtbootpcin01/tfstate/workloads/bank-compliance-ai-aks/prod.tfstate`
* **Provisioned Resources**:
  * `azurerm_resource_group`: `rg-ht-bankc-p-cin-01`
  * `module.bankc_vnet`: `vnet-ht-bankc-p-cin-01` (`10.42.0.0/16`)
  * `module.aks`: `aks-ht-bankc-p-cin-01` (Free Tier cluster node pool with Azure CNI Overlay)
  * `azurerm_user_assigned_identity`: Workload Identity for Kubernetes pods (OIDC federated credential)
  * `azurerm_cognitive_account`: Content Safety (`cs-ht-bankc-p-cin-01`)
  * `azurerm_static_web_app`: `stapp-ht-bankc-p-cin-01` (`Free` tier bound to custom domain **bank.mytaxbot.site**)

---

## 📁 Domain-Driven File Separation Architecture (Enterprise Standard)

Inside each Terraform deployment root (e.g., `platform/shared-services/`, `workloads/tax-advisor/`), resources are strictly partitioned into **domain-specific `.tf` files** rather than maintained as a single monolithic `main.tf`.

```
platform/shared-services/
├── main.tf              ── Resource Group foundation & CAF naming module invocations
├── networking.tf        ── Spoke VNet, Subnets, NSGs & Hub VNet Peering
├── security.tf          ── Key Vault, Access Policies & Managed Identities
├── observability.tf     ── Log Analytics Workspace, App Insights & Diagnostic Settings
├── api_management.tf    ── APIM Gateway instance & global API policies
├── ai_services.tf       ── Cognitive Services / Shared AI endpoints
├── locals.tf            ── Centralized tags, naming interpolation & local maps
├── variables.tf         ── Strongly-typed input variables with validation rules
├── outputs.tf           ── State outputs consumed by dependent workloads
├── versions.tf          ── Provider requirements (azurerm, azuread) and Terraform version pins
└── prod.tfvars          ── Environment-specific values
```

### Why Enterprises Enforce Domain File Separation

| Enterprise Driver | Monolithic `main.tf` (Anti-Pattern) | Domain-Driven File Splitting (Enterprise Standard) |
| :--- | :--- | :--- |
| **Git Merge Conflicts** | High — every team member edits the same file. | **Zero Conflicts** — Network, Security, and App engineers edit separate files concurrently. |
| **Code Review (PR) Focus** | Poor — reviewers must sift through 2,000+ lines. | **Atomic & Focused** — Security teams review `security.tf`, Network teams review `networking.tf`. |
| **Cognitive Load** | High — difficult to navigate resource relationships. | **Low & Intuitive** — Clean single-responsibility separation per domain. |
| **Execution Performance** | Identical | **Identical** — Terraform evaluates all `.tf` files in a folder into a single unified graph in memory. |

---

## 🔑 Backend Configuration Standard (`backend.hcl`)

All `backend.hcl` files across all roots must point `subscription_id` to the **Bootstrap Subscription**:

```hcl
# Standard backend.hcl pattern across all platform roots
resource_group_name  = "rg-ht-boot-p-cin-01"
storage_account_name = "sthtbootpcin01"
container_name       = "tfstate"
key                  = "workloads/tax-advisor/prod.tfstate"
subscription_id      = "7689ad81-71ba-481b-a17c-e1b6be61bab1" # Always Bootstrap subscription ID
use_azuread_auth     = true
```

> [!NOTE]
> `use_azuread_auth = true` ensures authentication to the state storage account uses Entra ID RBAC tokens (Storage Blob Data Contributor). Storage access keys are completely disabled for enhanced security.
