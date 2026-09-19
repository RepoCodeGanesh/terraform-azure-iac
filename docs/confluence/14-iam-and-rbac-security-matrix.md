# 14. Enterprise Identity & Access Management (IAM) & RBAC Security Matrix

## 1. Metadata & Governance
* **Document ID:** SPEC-IAM-014
* **Architecture Tier:** Identity, Security & Zero-Trust Governance
* **Tenant ID:** `4cef0d84-84d6-4ed0-8abe-773b015bcf99` (HappyTechies Cloud)
* **Author / Tech Lead:** Enterprise Platform Engineering Team
* **Source Path:** `docs/confluence/14-iam-and-rbac-security-matrix.md`
* **Status:** Approved / Production-Hardened

---

## 2. Executive Overview & Zero-Trust IAM Philosophy
In modern cloud and AI platforms, **Identity is the new security perimeter**. The HappyTechies Cloud & AI Platform operates under a strict **Zero-Trust Model** ("Never trust, always verify").

### Core IAM Architecture Tenets:
1. **Zero Static Credentials in CI/CD:** No long-lived Service Principal client secrets or publish profiles are stored in GitHub Secrets or Azure DevOps. All deployment pipelines authenticate dynamically via **Workload Identity Federation (WIF) OIDC**.
2. **Strict Plane Separation (Control Plane vs. Data Plane):** Azure Resource Manager (ARM) roles (e.g. `Owner`, `Contributor`) are never conflated with storage or database data-plane permissions. Data access requires explicit Azure RBAC data roles (e.g., `Storage Blob Data Contributor`, `Key Vault Secrets User`).
3. **Workload Identity Federation for Kubernetes (AKS Pods):** Containerized pods authenticate to Azure APIs using Kubernetes ServiceAccounts federated directly with Azure User-Assigned Managed Identities (UAMI), eliminating connection strings inside pods.
4. **Principle of Least Privilege (PoLP):** Service Principals and Managed Identities are scoped to minimum required resources and subscriptions.

---

## 3. Entra ID Workload Identity Federation (CI/CD Service Principals)

Each subscription in the Cloud Adoption Framework (CAF) hierarchy is assigned a dedicated Entra ID App Registration configured with Federated Identity Credentials (FIC):

```
+----------------------------------------------------------------------------------------------------+
|                                    Entra ID Tenant (4cef0d84...)                                   |
+----------------------------------------------------------------------------------------------------+
       |                                |                               |                        |
       v                                v                               v                        v
+------------------+     +--------------------+     +-----------------------+     +-------------------+
|  sp-bootstrap    |     |    sp-hub-prod     |     |  sp-shared-services   |     |    sp-apps-prod   |
| (934ab83b-...)   |     |   (78960c14-...)   |     |    (580ffcfd-...)     |     |   (99ab7987-...)  |
+------------------+     +--------------------+     +-----------------------+     +-------------------+
       |                                |                               |                        |
  Scope: Bootstrap sub            Scope: Hub sub             Scope: Shared sub            Scope: Apps sub
  (7689ad81-...)                  (3eb8cc01-...)              (859a785c-...)               (f4ffefe1-...)
```

### CI/CD Service Principal Matrix

| Component / Sub | Target Subscription | App Registration Client ID | Enterprise App Object ID | Primary Role | Federated Credential Subject |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Platform Bootstrap** | `bootstrap`<br>`7689ad81-...` | `934ab83b-2f61-475e-bdbc-85c9eaed83e6` | `f3a1b19b-11b8-4e13-8499-7f83ea39547a` | `Contributor` + `Storage Blob Data Contributor` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:bootstrap-prod` |
| **Platform Hub** | `Hub-prod`<br>`3eb8cc01-...` | `78960c14-26d2-4a0c-ab21-579c3030155e` | `14cfc7b4-c3a2-4994-9f5c-0ce4d8db0f57` | `Network Contributor` + `Contributor` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:hub-prod` |
| **Platform Shared** | `Shared-services`<br>`859a785c-...` | `580ffcfd-51ee-4dc3-9204-d03cb438ff82` | `c5a24473-2bad-41a7-b0b1-b79b94621252` | `Contributor` + `Key Vault Administrator` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:shared-services-prod` |
| **Workload Apps** | `Apps-prod`<br>`f4ffefe1-...` | `99ab7987-3989-46c3-bae9-92279be16608` | `9630f661-27e7-42f0-8377-5565ba7db7cd` | `Contributor` + `Storage Blob Data Contributor` | `repo:RepoCodeGanesh/terraform-azure-iac:environment:bank-compliance-prod` |

---

## 4. Kubernetes Workload Identity (Pod-to-Azure OIDC Federation)

In BankCompliance AI (`workloads/bank-compliance-ai-aks`), application pods interact with Azure Cognitive Services, Content Safety, and Storage without storing API keys in Kubernetes secrets.

### Authentication Flow:
```
+----------------------------------------------------------------------------------------------------+
|  Kubernetes Pod (bankc-backend)                                                                    |
|  1. ServiceAccount mounts projected SAT token (/var/run/secrets/tokens/azure-identity-token)      |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   | 2. Exchange JWT for Entra ID Access Token
                                                   v
+----------------------------------------------------------------------------------------------------+
|  Microsoft Entra ID (OIDC Federation)                                                             |
|  - Issuer URL: https://centralindia.oic.prod-aks.azure.com/.../                                    |
|  - Audience: api://AzureADTokenExchange                                                            |
|  - Subject: system:serviceaccount:bank-compliance:bankc-sa                                         |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   | 3. Returns OAuth2 Bearer Token
                                                   v
+----------------------------------------------------------------------------------------------------+
|  Azure Data Plane Services (Azure OpenAI / Content Safety / Blob Storage)                          |
|  - Validates role: Cognitive Services OpenAI Contributor / Storage Blob Data Contributor          |
+----------------------------------------------------------------------------------------------------+
```

### UAMI & FIC Definitions:
* **User-Assigned Managed Identity:** `uami-ht-bankc-p-cin-01`
* **Federated Identity Credential:** `fic-ht-bankc-p-cin-01`
* **Kubernetes ServiceAccount:** `bankc-sa` in namespace `bank-compliance`
* **Role Assignments:**
  * `Cognitive Services OpenAI Contributor` on Azure OpenAI account.
  * `Cognitive Services User` on Content Safety account.
  * `Storage Blob Data Reader` on `sthtbankcpcin01` (PDF Lake).

---

## 5. Control Plane vs. Data Plane RBAC Separation

A foundational learning in enterprise Azure architecture is that **Control Plane roles do NOT confer Data Plane permissions**:

```
+------------------------------------+          +------------------------------------+
|        Control Plane (ARM)         |          |             Data Plane             |
| Management & Resource Provisioning |          |      Data Operations & Payload     |
+------------------------------------+          +------------------------------------+
| Roles:                             |          | Roles:                             |
| - Owner                            |          | - Storage Blob Data Contributor    |
| - Contributor                      |          | - Storage Blob Data Reader         |
| - Reader                           |          | - Key Vault Secrets Officer        |
| - Network Contributor              |          | - Key Vault Secrets User           |
|                                    |          | - Cosmos DB Built-in Data Reader   |
+------------------------------------+          +------------------------------------+
```

### Key Incident Learning (Troubleshooting Learning #21):
* **Symptom:** CI/CD deployment failed with `403 AuthorizationPermissionMismatch` when synchronizing statutory PDFs to Azure Blob Storage via AzCopy / Azure AD.
* **Root Cause:** The Service Principal held `Contributor` on the subscription, but Azure Storage enforces data plane RBAC.
* **Remediation:** Explicitly grant `Storage Blob Data Contributor` to the deployment identity on the storage account scope.

---

## 6. Key Vault Access Model: Azure RBAC vs. Access Policies

All platform Key Vaults enforce modern **Azure Role-Based Access Control (RBAC)** mode (`enable_rbac_authorization = true`), replacing legacy access policies:

| Security Requirement | Role Assigned | Assignee Identity | Scope |
| :--- | :--- | :--- | :--- |
| **CI/CD Token Ingestion** | `Key Vault Secrets Officer` | Deployment Service Principal (`app-prod`) | Workload Key Vault (`kv-ht-taxb-p-cin-01`) |
| **Function App Secret Retrieval** | `Key Vault Secrets User` | System-Assigned Identity (`func-ht-taxb-p-cin-01`) | Workload Key Vault (`kv-ht-taxb-p-cin-01`) |
| **AKS CSI Secret Provider** | `Key Vault Secrets User` | User-Assigned Identity (`uami-aks-...`) | Shared Key Vault (`kv-ht-ss-p-cin-01`) |
| **Platform Administrator** | `Key Vault Administrator` | Central Platform Admin (`PrimaryAdmin`) | Shared Key Vault (`kv-ht-ss-p-cin-01`) |

---

## 7. Audit & Compliance Governance Verification

1. **Continuous Entra ID Audit Ingestion:**
   All authentication events, service principal sign-ins, and role assignments stream continuously to `law-ht-ss-p-cin-01` via diagnostic settings.
2. **KQL Audit Query for Role Changes:**
   ```kql
   AzureActivity
   | where OperationNameValue has "Microsoft.Authorization/roleAssignments/write"
   | project TimeGenerated, Caller, CallerIpAddress, Properties
   | order by TimeGenerated desc
   ```
3. **Secret Rotation Policy:**
   Automated 90-day expiry enforcement via Azure Policy, alerting to `ag-ht-ss-p-cin-01` on impending credential expirations.
