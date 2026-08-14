# 🏷️ Enterprise Naming & Tagging Standards Specification

* **Document Code:** `STD-HT-CLOUD-NAMING-01`
* **Space:** `HappyTechies Cloud & AI Platform` $\rightarrow$ `Governance & Standards`
* **Status:** `MANDATORY / ENTERPRISE STANDARD`
* **Applies To:** All Azure Subscriptions, Terraform Modules, Kubernetes Clusters, and Workloads

---

## 🎯 1. Purpose & Strategy Rationale

In enterprise cloud environments, inconsistent resource naming causes operational confusion, billing misallocation, security audit failures, and automated script breakage. **HappyTechies** enforces a strict, deterministic naming and tagging standard based on the **Microsoft Cloud Adoption Framework (CAF)**.

### Why this Naming Strategy was Chosen:
1. **Deterministic & Scriptable:** Every resource name reveals its resource type, project, workload, environment, Azure region, and instance number without needing to query cloud metadata.
2. **Azure Constraint Resilient:** Automatically handles Azure's diverse naming rules (e.g. Storage Accounts requiring 3-24 lowercase alphanumeric chars with no hyphens vs. Resource Groups allowing hyphens).
3. **Multi-Subscription Blast Radius Control:** Guarantees zero name collisions across subscriptions while enabling seamless cross-subscription lookups.
4. **Automated FinOps Cost Tracking:** Mandatory tagging enables granular cost-center chargebacks down to the exact workload.

---

## 📐 2. Enterprise Naming Schemas

### A. Hyphenated Standard Schema (Default for 95% of Resources)
Used for Resource Groups, VNets, Subnets, AKS Clusters, Functions, Cognitive Services, Key Vaults, APIM:

$$\text{Format: } \mathbf{\langle resource\_type\rangle\text{-}\langle project\rangle\text{-}\langle workload\rangle\text{-}\langle environment\rangle\text{-}\langle region\_short\rangle\text{-}\langle instance\rangle}$$

* **Example Resource Group:** `rg-ht-bankc-p-cin-01`
* **Example AKS Cluster:** `aks-ht-bankc-p-cin-01`
* **Example VNet:** `vnet-ht-taxb-p-cin-01`
* **Example Function App:** `func-ht-taxb-p-cin-01`
* **Example Content Safety:** `cs-ht-bankc-p-sea-01`

---

### B. Compact Schema (Hyphen-Free)
Used strictly for resources that forbid hyphens or enforce tight character limits (Storage Accounts, Container Registries):

$$\text{Format: } \mathbf{\langle resource\_type\rangle\langle project\rangle\langle workload\rangle\langle environment\rangle\langle region\_short\rangle\langle instance\rangle}$$

* **Example Bootstrap Storage:** `sthtbootpcin01`
* **Example TaxBot Storage:** `sthttaxbpcin01`
* **Example Container Registry:** `acrhtbankcpcin01`

---

## 📚 3. Standard Abbreviation Dictionaries

### Resource Types (`resource_type`)
| Abbreviation | Azure Resource Type |
| :--- | :--- |
| `rg` | Resource Group |
| `vnet` | Virtual Network |
| `snet` | Subnet |
| `aks` | Azure Kubernetes Service Cluster |
| `st` | Storage Account |
| `func` | Azure Function App (Linux) |
| `asp` | App Service Plan |
| `stapp` | Azure Static Web App |
| `oai` | Azure OpenAI Cognitive Service |
| `cs` | Azure AI Content Safety Service |
| `srch` | Azure AI Search Service |
| `cosmos` | Azure Cosmos DB Account |
| `apim` | API Management Gateway |
| `law` | Log Analytics Workspace |
| `appi` | Application Insights Instance |
| `kv` | Azure Key Vault |
| `uami` | User-Assigned Managed Identity |
| `fic` | Federated Identity Credential (OIDC) |
| `pip` | Public IP Address |
| `nsg` | Network Security Group |

---

### Environments (`environment`)
| Code | Environment Name |
| :--- | :--- |
| `d` | Development / Sandbox |
| `t` | Testing / QA |
| `s` | Staging / UAT |
| `p` | Production |

---

### Workloads (`workload`)
| Code | Workload / Platform Domain | Target Scope |
| :--- | :--- | :--- |
| `boot` | Platform Bootstrap & Remote State | `platform/bootstrap` |
| `hub` | Central Network Hub & Central Routing | `platform/hub` |
| `ss` | Shared Services (LAW, APIM, Key Vault) | `platform/shared-services` |
| `taxb` | TaxBot India AI Tax Advisor | `workloads/tax-advisor` |
| `bankc` | BankCompliance AI Copilot on AKS | `workloads/bank-compliance-ai-aks` |

---

### Azure Regions (`region_short`)
| Short Code | Azure Region Name | Primary Usage |
| :--- | :--- | :--- |
| `cin` | Central India (Pune) | Primary Region for Compute, Storage & Data |
| `sea` | Southeast Asia (Singapore) | Azure AI Content Safety `F0` Free Tier |
| `eus` | East US (Virginia) | Azure OpenAI `gpt-5.4-nano` & Static Web App Control Plane |
| `eus2` | East US 2 | Static Web App Secondary Region |

---

## 🏷️ 4. Mandatory Enterprise Tagging Policy

Every resource provisioned via Terraform must inherit the unified tagging policy defined in `locals.tf`:

```hcl
locals {
  tags = {
    Company     = "HappyTechies"
    Project     = "ht"
    Workload    = var.workload
    Environment = var.environment
    Owner       = "ai-platform-team@happytechies.com"
    CostCenter  = "CC-AI-PLATFORM-01"
    ManagedBy   = "Terraform"
  }
}
```

### Tagging Validation & Enforcement Rules:
1. **Azure Policy Enforcement:** Azure Policy denies creation of any resource lacking `ManagedBy`, `Environment`, or `CostCenter`.
2. **FinOps Billing Attribution:** Automated monthly Azure Cost Management reports aggregate expenditures by `CostCenter` and `Workload`.
3. **Compliance Auditing:** Untagged resources trigger immediate alerts in central Log Analytics.
