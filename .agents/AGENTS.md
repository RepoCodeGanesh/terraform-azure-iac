# Repository Configuration & AI Agent Context

## Purpose
This is the **Enterprise Azure Landing Zone monorepo** for HappyTechies Cloud & AI Platform.
It contains all Terraform infrastructure, Azure DevOps pipelines, and application code for all workloads.

---

## Workspace Layout

```
terraform-azure-iac/
├── platform/
│   ├── governance/         # Enterprise Management Groups & Policy-as-Code (HappieTechies-root-MG)
│   ├── bootstrap/          # Bootstrap sub (7689ad81) — remote state SA, Key Vault
│   ├── hub/                # Hub-prod sub (3eb8cc01) — Azure Firewall, Bastion, Gateway
│   └── shared-services/    # Shared-services sub (859a785c) — APIM, Log Analytics, Key Vault
├── workloads/
│   ├── tax-advisor/        # TaxBot IaC — Apps-prod sub (f4ffefe1)
│   └── bank-compliance-ai-aks/ # BankCompliance IaC — Apps-prod sub (f4ffefe1)
├── app/
│   ├── tax-advisor/        # TaxBot app code (React + Python Function App)
│   └── bank-compliance/    # BankCompliance app code (React + FastAPI + k8s manifests)
│       ├── backend/        # FastAPI backend + Dockerfile
│       ├── frontend/       # React Vite SPA (bank.mytaxbot.site)
│       ├── k8s/            # All Kubernetes manifests (namespace, SA, deployments, KEDA)
│       ├── chart/          # Helm chart package
│       ├── eval/           # CI/CD evaluation & golden dataset
│       └── .github/workflows/ # GitHub Actions CI/CD
├── modules/                # Reusable Terraform modules
├── pipelines/              # Azure DevOps pipeline YAMLs + reusable templates
└── docs/                   # Architecture docs, guides, planning docs
```

---

## Management Group & Subscription Map (CAF Enterprise Hierarchy)

* **Root MG:** `HappieTechies-root-MG` (`HappyTechies Root`)
  * **Platform MG (`mg-ht-platform`):**
    * `bootstrap` (`7689ad81-71ba-481b-a17c-e1b6be61bab1`)
    * `Hub-prod` (`3eb8cc01-50c6-473e-8d5f-f8d532ae1f5b`)
    * `Shared-services` (`859a785c-bd38-402d-b595-1f44f40fb9bf`)
  * **Landing Zones MG (`mg-ht-landingzones`):**
    * `Apps-prod` (`f4ffefe1-d689-4059-969c-ccc73e2a11d4`)

Tenant ID: `4cef0d84-84d6-4ed0-8abe-773b015bcf99`

---

## Active Workloads

### Workload 1: TaxBot India
- **Domain:** https://www.mytaxbot.site
- **IaC:** `workloads/tax-advisor/`
- **App:** `app/tax-advisor/`
- **CI/CD:** `pipelines/azure-cicd-tax-advisor.yml` + `.github/workflows/workload-tax-advisor.yml` / `app-tax-advisor.yml`

### Workload 2: BankCompliance AI
- **Domain:** https://bank.mytaxbot.site
- **IaC:** `workloads/bank-compliance-ai-aks/`
- **App:** `app/bank-compliance/`
- **CI/CD:** `pipelines/azure-cicd-bank-compliance-aks.yml` + `app/bank-compliance/.github/workflows/build-and-deploy.yml` / `.github/workflows/app-bank-compliance.yml`
- **Stack:** AKS Free Tier (`aks-ht-bankc-p-cin-01`), LiteLLM Proxy, Qdrant (4GB CSI disk), KEDA scale-to-zero
- **Key IaC Outputs needed by app:**
  - `aks_workload_identity_client_id` → annotate `k8s/serviceaccount.yaml`
  - `content_safety_endpoint` → set in `k8s/backend-configmap.yaml`
  - `static_web_app_api_key` → GitHub Secret `AZURE_STATIC_WEB_APPS_API_TOKEN`

---

## CI/CD Authentication (Workload Identity Federation)

| ADO Service Connection | GitHub Secret | App Registration Client ID | Enterprise App Object ID (Principal ID) |
|----------------------|---------------|---------------------------|------------------------------------------|
| `bootstrap` | `BOOTSTRAP_CLIENT_ID` | `934ab83b-2f61-475e-bdbc-85c9eaed83e6` | `f3a1b19b-11b8-4e13-8499-7f83ea39547a` |
| `hub-prod` | `HUB_CLIENT_ID` | `78960c14-26d2-4a0c-ab21-579c3030155e` | `14cfc7b4-c3a2-4994-9f5c-0ce4d8db0f57` |
| `shared-services` | `SHARED_CLIENT_ID` | `580ffcfd-51ee-4dc3-9204-d03cb438ff82` | `c5a24473-2bad-41a7-b0b1-b79b94621252` |
| `app-prod` | `APP_CLIENT_ID` | `99ab7987-3989-46c3-bae9-92279be16608` | `9630f661-27e7-42f0-8377-5565ba7db7cd` |

GitHub Secrets required for BankCompliance GHA: `APP_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_STATIC_WEB_APPS_API_TOKEN`

---

## Terraform State (Remote — Azure Blob)

All roots use Azure AD auth (`use_azuread_auth = true`) against `sthtbootpcin01` in the bootstrap subscription.
State files are path-keyed — **git repo location does not affect state**.

| Root | State Key |
|------|-----------|
| `platform/governance` | `governance/prod.tfstate` |
| `platform/bootstrap` | `bootstrap/prod.tfstate` |
| `platform/hub` | `hub/prod.tfstate` |
| `platform/shared-services` | `shared-services/prod.tfstate` |
| `workloads/tax-advisor` | `workloads/tax-advisor/prod.tfstate` |
| `workloads/bank-compliance-ai-aks` | `workloads/bank-compliance-ai-aks/prod.tfstate` |

---

## Agent Rules

1. **Continuous Documentation Maintenance:** Always proactively update project documentation (`AGENTS.md`, READMEs, architecture runbooks, and roadmap docs) whenever code, infrastructure, workflows, or policies change.
2. When working on `app/bank-compliance/`, always cross-check `workloads/bank-compliance-ai-aks/outputs.tf` for resource names and endpoints that must be wired into k8s ConfigMaps.
3. Never hardcode subscription IDs — use `${{ secrets.AZURE_SUBSCRIPTION_ID }}` in GHA and `var.subscription_id` in Terraform.
4. Terraform roots are independent — do not merge state files or add cross-root `terraform_remote_state` without explicit instruction.
5. The ADO environment for BankCompliance infra approvals is `bank-compliance-prod`. Do not use `tax-advisor-prod`.
6. LiteLLM image must be pinned to a specific version tag — never use `:main-latest`.
7. **Document All Incident Learnings:** Whenever a bug, workflow failure, or edge-case is resolved, immediately add the root cause and remediation steps to the Troubleshooting section below.
8. **Visual Presentation Standard:** Prefer clean ASCII box diagrams, Unicode structured flowcharts, and comparative Markdown tables over raw Mermaid blocks to guarantee 100% reliable rendering across all chat interfaces, IDE panels, and web viewers.
9. **Frequent Documentation & Confluence Maintenance:** Proactively update local markdown docs (`docs/confluence/`, `README.md`, `PROJECT_CONTEXT.md`) and keep live Atlassian Confluence (`HT` space) synchronized whenever code, infrastructure, or policies evolve.

---

## 🛠️ Operational Troubleshooting & Engineering Learnings

### 1. GitHub Actions: `Unrecognized named-value: 'matrix'` at Job Level
* **Symptom:** Workflow fails parsing with `Unrecognized named-value: 'matrix' @[L43]`.
* **Root Cause:** Job-level `if:` conditions (`jobs.<job>.if`) evaluate *before* `strategy.matrix` is expanded. The `matrix` context is not available at the job root.
* **Resolution:** Implement a preliminary `resolve-targets` setup job that evaluates the target input and outputs a dynamically filtered matrix JSON array (`include: ${{ fromJson(needs.resolve-targets.outputs.matrix) }}`).

### 2. GitHub Actions: Multiline `$GITHUB_OUTPUT` Parse Failure
* **Symptom:** Runner error: `##[error]Unable to process file command 'output' successfully. Invalid format '  {"name":...'`.
* **Root Cause:** GitHub Actions `$GITHUB_OUTPUT` expects single-line `key=value` pairs. Unescaped multiline strings break parsing on line 2.
* **Resolution:** Format matrix JSON as a compact single-line string (`ALL_TARGETS='[{"name":"..."},...]'`) or use EOF delimiter syntax (`echo "matrix<<EOF" >> $GITHUB_OUTPUT`).

### 3. Dynamic Secret Indexing is Unsupported in GitHub Actions
* **Symptom:** `${{ secrets[matrix.secret_name] }}` evaluates to empty/null or fails.
* **Root Cause:** GitHub Actions does not support dynamic bracket dereferencing on the `secrets` context.
* **Resolution:** Pass public Entra ID Client IDs directly inside the matrix objects (`client_id: '934ab83b-...'`) rather than indexing secrets.

### 4. Multi-Agent Semantic Drift & Hallucination Loop on Off-Topic Queries
* **Symptom:** Asking `"how to fly in sky"` caused the AI to synthesize a detailed answer on NRI KYC V-CIP.
* **Root Cause:** When initial vector search returned 0 results, the Auditor Agent reflection loop injected a generic domain search query (`"RBI Master Direction on kyc"`), pulling unrelated documents into context and forcing synthesis.
* **Resolution:** Enforce a deterministic out-of-scope guardrail in `SupervisorAgent` to immediately reject non-banking queries in `<10ms` before entering vector retrieval or reflection loops.

### 5. Grafana ClusterIP & Public HTTPS Mixed Content
* **Symptom:** Embedded Grafana iframe fails to load or appears empty on `https://bank.mytaxbot.site`.
* **Root Cause:** Web browsers block embedding local/HTTP services (`http://localhost:3000`) inside secure HTTPS origins. Furthermore, Grafana is intentionally kept as internal `ClusterIP` in the `monitoring` namespace for security & zero egress cost.
* **Resolution:** Render native React telemetry panels on the website. To access full Grafana UI, use secure local port-forwarding: `kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring`.

### 6. Terraform Backend Partial Configuration
* **Symptom:** `terraform init` fails with backend configuration missing errors.
* **Root Cause:** Monorepo uses partial backend definitions with empty `backend "azurerm" {}` in `versions.tf`.
* **Resolution:** Always initialize Terraform with `-reconfigure -backend-config=backend.hcl -input=false` and set `ARM_USE_OIDC: "true"`.

### 7. GitHub Actions Expression Syntax: Unexpected Symbol / Escaped Quotes
* **Symptom:** Workflow parse failure `Unexpected symbol: '\"...'. Located at position X within expression: ${{ inputs.param || \"...\" }}`.
* **Root Cause:** GitHub Actions expressions (`${{ ... }}`) require single quotes (`'...'`) for string literals. Double quotes (`"..."`) or escaped quotes (`\"...\"`) are invalid within expressions. Furthermore, directly interpolating `${{ ... }}` into inline scripts (Python/Bash) risks script injection and string delimiter clashes.
* **Resolution:** In expressions, always use single quotes (`${{ inputs.param || 'default-value' }}`). For inline scripts, pass variables via step-level `env:` and access them via `os.environ` or `$ENV_VAR`.

### 8. Azure Cognitive Services Soft-Delete & `FlagMustBeSetForRestore` Collision
* **Symptom:** `azapi_resource` creation for Azure OpenAI or Content Safety fails with `409 Conflict: FlagMustBeSetForRestore` ("An existing resource with ID '...' has been soft-deleted. To restore it, set the restore flag to true").
* **Root Cause:** Deleting an Azure Cognitive Services / OpenAI account places it into a soft-deleted retention state (48 hours to 90 days). ARM / AzAPI resource creation requests (`PUT`) fail because the resource name remains locked in the subscription's recycle bin.
* **Resolution:** Purge the soft-deleted resource from the recycle bin before re-running Terraform apply:
  ```bash
  az cognitiveservices account purge --name <account-name> --resource-group <rg-name> --location <location> --subscription <sub-id>
  ```

### 9. Key Vault Secrets & RBAC Role Assignment 409 Conflicts Missing from State
* **Symptom:** `azurerm_key_vault_secret` or `azurerm_role_assignment` fails with `409 Conflict: A secret with ID ... already exists` or `RoleAssignmentExists`.
* **Root Cause:** Cloud resources were manually provisioned or left behind from a previous destroyed state while the remote state file was deleted or out-of-sync.
* **Resolution:** For Key Vault secrets, delete and purge soft-deleted secrets (`az keyvault secret delete` and `az keyvault secret purge`). For role assignments, remove orphaned assignments using `az role assignment delete --ids <id>` or import them into Terraform state (`terraform import <resource> <id>`).

### 10. AKS Diagnostic Setting Pre-existence & Terraform State Collision
* **Symptom:** `azurerm_monitor_diagnostic_setting` fails with `already exists - to be managed via Terraform this resource needs to be imported into the State`.
* **Root Cause:** When an AKS cluster is deployed with OMS agent or policy enforcement, Azure Monitor diagnostic settings (`diag-aks-ht-bankc-p-cin-01`) may be created directly in ARM or exist from earlier unmanaged runs.
* **Resolution:** Import the diagnostic setting into the Terraform state:
  ```bash
  terraform import -var-file="prod.tfvars" 'module.bank_compliance_aks.azurerm_monitor_diagnostic_setting.aks_diagnostics[0]' '/subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/Microsoft.ContainerService/managedClusters/<cluster-name>|<diag-name>'
  ```

### 11. GitHub Actions: Job Depends on Unknown Job in `needs:` Array
* **Symptom:** Workflow parse failure: `Invalid workflow file: ... Job 'summary' depends on unknown job 'deploy-backend-aks'`.
* **Root Cause:** A downstream aggregation or summary job lists a job ID in `needs:` that does not match the exact key name defined under `jobs:` in the workflow YAML.
* **Resolution:** Synchronize the job key in `jobs:` (e.g., rename `deploy-aks:` to `deploy-backend-aks:`) to match all downstream `needs:` references.

### 12. AKS Stopped State Mutation Restrictions (`OperationNotAllowed`)
* **Symptom:** Terraform apply or ARM mutation fails with `400 Bad Request: OperationNotAllowed: Managed Cluster is in stopped state, no operations except for start are allowed`.
* **Root Cause:** For FinOps cost optimization, AKS clusters may be powered down (`Stopped`). Azure Resource Manager forbids any cluster updates, node pool upgrades, or addon mutations while stopped.
* **Resolution:** Start the AKS cluster (`az aks start --name <cluster> --resource-group <rg>`) and wait for `provisioningState: Succeeded` before applying Terraform changes.

### 13. Static Web App Deployment Token Misalignment (`Reason: No matching Static Web App was found or the api key was invalid`)
* **Symptom:** `Azure/static-web-apps-deploy@v1` fails with HTTP 400 `BadRequest: No matching Static Web App was found or the api key was invalid`.
* **Root Cause:** In caller workflows calling reusable `app-deploy-swa.yml`, `swa_token_secret_name` was omitted and defaulted to a legacy uppercase secret name (`SWA-TAXB-DEPLOYMENT-TOKEN`) containing an obsolete token, whereas Terraform stores the live API key in `taxb-swa-deployment-token`.
* **Resolution:** Explicitly pass `swa_token_secret_name: 'taxb-swa-deployment-token'` in the caller workflow `with:` block and ensure Key Vault secrets reflect the live `az staticwebapp secrets list` API token.

### 14. AKS Ingress Public IP Elimination via Internal Web App Routing
* **Symptom:** AKS Web App Routing addon provisions an unwanted public IP (`kubernetes-*`) on the NGINX ingress controller incurring hourly static IP charges (~$3.65/mo).
* **Root Cause:** By default, AKS Web App Routing initializes NGINX with `defaultIngressControllerType: External` creating a public Azure Load Balancer frontend.
* **Resolution:** Reconfigure App Routing to internal mode via Azure CLI (`az aks approuting update --nginx Internal --name <cluster> --resource-group <rg>`) or set `loadBalancerAnnotations: { "service.beta.kubernetes.io/azure-load-balancer-internal": "true" }` on the `NginxIngressController` CRD. Azure automatically deletes the public IP and unbinds the frontend.

### 15. GitHub Actions: `Workflow does not exist or does not have a workflow_dispatch trigger in this branch`
* **Symptom:** In GitHub Actions UI, clicking **Run workflow** displays yellow warning: `Workflow does not exist or does not have a workflow_dispatch trigger in this branch` with the button disabled.
* **Root Cause:** GitHub Actions UI caches the historical YAML filename (e.g. `terraform-unified-manager.yml`). If the file was renamed in a feature branch (e.g. to `ops-terraform-manager.yml`), GitHub checks the branch for the exact historical filename and fails if it doesn't match.
* **Resolution:** Ensure the exact YAML filename expected by the UI (`terraform-unified-manager.yml`) exists in the branch with a valid `workflow_dispatch:` trigger.

---

## 🚀 AI Platform Engineering, GenAIOps, LLMOps & DataOps Core Competencies

### 1. 🏗️ AI Platform Engineering (Azure CAF & Zero-Trust Cloud)
* **Topology:** 4-Subscription CAF Enterprise Landing Zone (`bootstrap`, `hub`, `shared-services`, `apps-prod`).
* **Identity & Security:** Entra ID Workload Identity Federation (WIF) OIDC authentication for GitHub Actions & Azure DevOps. Zero static secrets.
* **FinOps Discipline:** $0.00 idle compute profile using AKS Free Tier, Ephemeral OS, SWA Free Tier, and Consumption Serverless.

### 2. ⚡ GenAIOps & Multi-Agent RAG Orchestration
* **Architecture:** 4-Microagent State Graph (Supervisor Router ➔ Retriever ➔ Auditor Reflection Critic ➔ Synthesizer).
* **FinOps & Speed:** Sub-10ms Governed Semantic Vector Cache with 94.2% hit rate ($0.0035/query cost reduction).
* **High Availability:** Multi-Cloud AI Gateway (LiteLLM) routing to Google Gemini 2.0 Flash with automated failover to Azure OpenAI `gpt-5.4-nano` on HTTP 429.

### 3. 🔍 LLMOps & Quality Guardrails
* **Continuous Evaluation:** Automated CI/CD evaluation gate with Ragas Triad metrics (Groundedness 4.68/5.0, Citation Integrity 4.92/5.0, Answer Relevance 4.46/5.0).
* **Data Protection:** Real-time DPDP Act PII Sanitization (PAN, Aadhaar, Card numbers auto-masked).
* **Safety Shields:** Deterministic domain out-of-scope interceptor (<10ms) to prevent hallucination / semantic drift loops.

### 4. 📊 DataOps & Regulatory Data Lake
* **Ingestion:** Automated PDF layout-aware chunking pipeline with SHA-256 cryptographic provenance hashing for auditable citations.
* **Vector Store:** Qdrant Vector Store on AKS with 4GB Managed CSI Persistent Disk and HNSW indexing.

### 5. 🛡️ DevSecOps & Policy-as-Code (Checkov IaC Security)
* **Scanner:** Checkov (Palo Alto / Bridgecrew) Static Code Analysis & Policy-as-Code.
* **Config:** Central repository configuration at `.checkov.yaml` with framework targets `[terraform, kubernetes]`.
* **Rollout Strategy:**
  - **Phase 1: Discovery (Week 1)**: Advisory mode (`soft_fail: true`). Scans all platform & workload IaC PRs, outputs markdown summaries to `$GITHUB_STEP_SUMMARY`, and uploads SARIF findings to GitHub Security tab without blocking deployments.
  - **Phase 2: Baseline (Week 2)**: Create baseline suppression file for existing architectural trade-offs.
  - **Phase 3: Enforcement (Week 3+)**: Enforce blocking gate (`soft_fail: false`) for new CRITICAL/HIGH violations.
* **Inline Waivers:** When suppressing an accepted violation, use `#checkov:skip=CKV_AZURE_XX: "Documented justification"`.

### 6. 📦 Reusable Module Architecture Philosophy (AVM Wrappers vs. Hardened Native)
* **Architecture Pattern:** Hybrid CAF modularization calling official `hashicorp/azurerm ~> 4.0` provider.
* **AVM Wrappers:** Used for standalone single-purpose services with mature Microsoft schemas (`modules/search_service` wrapping `Azure/avm-res-search-searchservice/azurerm`).
* **Hardened Native Modules:** Used for core compute, networking, and security (`modules/aks`, `modules/key_vault`, `modules/network`, `modules/function_app`, `modules/cosmos_db`, `modules/cognitive_account`, `modules/content_safety`, `modules/static_web_app`):
  - **FinOps Guardrails:** Enforces Free-tier SKUs (`Free`, `Y1`, `F0`, `Essential`), Ephemeral OS ($0.00), and KEDA scale-to-zero.
  - **WIF & OIDC Direct Binding:** Direct binding of Federated Identity Credentials and RBAC without fighting third-party module abstraction layers.
  - **Fast Execution:** Eliminates deeply nested module trees, executing CI/CD plans in < 15 seconds.

### 7. 🏛️ 5-Pillar Enterprise CAF Platform Standards ($0.00 / Ultra-Low Cost)
1. **FinOps Spend Protection:** $15 monthly budget guardrails (`azurerm_consumption_budget_subscription`) across all 4 subscriptions with email alerts at 70%, 90%, 100% to `richtextforganesh@outlook.com`.
2. **Centralized Observability:** Azure Managed Grafana (`sku = "Essential"` $0.00 / 30 users) in `platform/shared-services` with `Monitoring Reader` RBAC, Central Action Group (`ag-ht-ss-p-cin-01`), Resource Graph KQL inventory queries, and Azure Monitor Workbooks.
3. **Security Posture:** Microsoft Defender for Cloud Free CSPM (Continuous CIS Azure Foundations benchmark scanning) + Key Vault `AuditEvent` diagnostic streaming to `law-ht-ss-p-cin-01`.
4. **Zero-Trust Hybrid Networking:** Central Private DNS Zones in Hub (`privatelink.vaultcore.azure.net`, `cognitiveservices`, `search`) linked to Hub, Shared Services, and Apps Spoke VNets.
5. **Shared AI Platform Services:** Central Azure Document Intelligence (`F0` 500 pgs/mo free) and Azure AI Search (`free` 10k docs free) in `platform/shared-services` with endpoints wired to Key Vault and workload ConfigMaps.

---

## 🤖 Developer AI Tooling & Environment Context
- **Primary Focus:** Enterprise AI Platform Engineering, GenAIOps, LLMOps, and Cloud-Native DataOps.
- **AI Ecosystem:** Google AI Plus (Gemini Pro long-context analysis), Antigravity IDE, NotebookLM (regulatory PDF analysis), Azure AI Services.
- **Atlassian Confluence Space:** `HappyTechies Cloud & AI Platform` (`HT`) at `https://happytechies.atlassian.net/wiki/spaces/HT/overview`.
  - **Account Email:** `richtextforganesh@outlook.com`
  - **Secret Location:** Azure Key Vault `kv-ht-ss-p-cin-01` (secret: `confluence-api-token` in Shared Services sub `859a785c-bd38-402d-b595-1f44f40fb9bf`).
  - **Auto-Sync Script:** `scripts/sync_to_confluence.py` (converts markdown to storage XHTML and updates Space `HT` via REST API).


