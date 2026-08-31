# 10. Master Incident Post-Mortems & Root Cause Analysis (RCA)

**Document ID:** `CR-SRE-10`  
**Classification:** Enterprise SRE, DevOps & AI Platform Post-Mortems  
**Target Environment:** HappyTechies Enterprise Landing Zone & GenAIOps Applications  
**Status:** `LIVING KNOWLEDGE BASE / AUDITED`  

---

## 1. SRE Incident Severity Classification Framework

All platform incidents are triaged and documented using standard SRE severity tiers:

```text
+--------------------------------------------------------------------------------------------------+
|                                INCIDENT SEVERITY MATRIX                                          |
+--------------------------------------------------------------------------------------------------+
  [SEV-1 (CRITICAL)]: Full production outage, customer-facing downtime, or security breach.
  [SEV-2 (HIGH)]    : Degradation of core AI services, failed CI/CD deployments, or hallucination loops.
  [SEV-3 (MEDIUM)]  : Minor workflow warnings, non-blocking telemetry gaps, or transient API rate limits.
```

---

## 2. Master Incident Registry & Post-Mortem Index

| Incident ID | Severity | Incident Title | Subsystem Impacted | Root Cause Summary |
|:---:|:---:|:---|:---|:---|
| **INC-01** | `SEV-2` | GitHub Actions Dynamic Matrix Parse Failure (`matrix` context) | CI/CD Drift Workflow | Job-level `if:` evaluated before `strategy.matrix` expansion. |
| **INC-02** | `SEV-2` | Runner Output Corruption via Multiline `$GITHUB_OUTPUT` | CI/CD Runner Engine | Raw unescaped newlines in JSON broke `key=value` format. |
| **INC-03** | `SEV-2` | Dynamic Bracket Dereferencing on Secret Values (`secrets[var]`) | CI/CD Auth / WIF | GitHub Actions does not support runtime bracket indexing on secrets. |
| **INC-04** | `SEV-2` | Multi-Agent Semantic Drift & Hallucination Loop on Off-Topic Query | GenAIOps / Copilot | Reflection loop injected synthetic queries on 0-hit vector search. |
| **INC-05** | `SEV-3` | Embedded Grafana Iframe Blocked by Browser Mixed Content | Observability UI | Browser blocked embedding internal `http://localhost:3000` in HTTPS SWA. |
| **INC-06** | `SEV-2` | Oryx/Vite Build Failure via UTF-8 Byte Order Mark (BOM) in JSON | Frontend Build Pipeline | Windows Notepad invisible `\uFEFF` prefix corrupted PostCSS parser. |
| **INC-07** | `SEV-2` | Azure OpenAI API Incompatibility on `max_completion_tokens` | AI Gateway / LLM Proxy | Newer reasoning models rejected legacy `max_tokens` API parameter. |
| **INC-08** | `SEV-2` | AKS Pod Stale Image Caching on Mutable Container Tags (`:latest`) | Kubernetes Deployment | `imagePullPolicy: IfNotPresent` prevented fresh container downloads. |
| **INC-09** | `SEV-2` | APIM Gateway CORS Preflight Failure on Custom Auth Headers | API Gateway / APIM | Missing wildcard/specific allowed headers in APIM inbound XML policy. |
| **INC-10** | `SEV-2` | Terraform Init Backend Failure on Partial Reconfiguration | Terraform Monorepo | Monorepo empty `backend "azurerm" {}` required `-reconfigure` flag. |
| **INC-11** | `SEV-2` | Qdrant CSI Persistent Volume Mount Permission Lock | Vector DB / Storage | Managed disk locked to terminated node during AKS rescheduling. |
| **INC-12** | `SEV-3` | DPDP Act PII Sanitizer Catastrophic Regex Backtracking | Security / PII Shield | Nested greedy regex quantifiers spiked CPU to 100% on large inputs. |
| **INC-13** | `SEV-2` | Static Web App Deployment Token Misalignment | SWA CI/CD Pipeline | Reusable workflow defaulted to legacy secret name with obsolete token. |
| **INC-14** | `SEV-3` | AKS Ingress Public IP Elimination via Internal Web App Routing | AKS Networking | Default external ingress controller created unwanted public IP. |
| **INC-15** | `SEV-3` | GHA Workflow UI Disconnect on Feature Branch Rename | GitHub Actions UI | UI checked for historical YAML filename instead of renamed file. |
| **INC-16** | `SEV-2` | Reusable Workflow Permission Delegation Failure | GitHub Actions Security | Caller workflow omitted `actions: read` required by CodeQL upload. |
| **INC-17** | `SEV-2` | 3-Layer Mathematical Vector Centroid Guardrail Interception | AI Safety Engine | Handcrafted regex heuristics bypassed on short follow-up prompts. |
| **INC-18** | `SEV-2` | LiteLLM Routing Strategy Enterprise License Exception | AI Gateway Pod | `latency-based-routing` required enterprise license; crashed proxy. |
| **INC-19** | `SEV-2` | Domain Guardrail False Positives on Colloquial Banking Phrasing | AI Safety Engine | Unfiltered stopwords and sparse baseline centroid blocked loan queries. |
| **INC-20** | `SEV-2` | Azure Cognitive Services Soft-Delete Name Collision | Terraform IaC / ARM | Soft-deleted resource in recycle bin blocked recreating with same name. |
| **INC-21** | `SEV-2` | Azure Storage Authorization 403 on Entra ID Blob Sync | Entra ID RBAC / WIF | ARM Contributor role lacked explicit data plane Blob Contributor RBAC. |
| **INC-22** | `SEV-1` | Helm Upgrade Timeout on AKS Workload Identity Webhook Deadlock | Kubernetes Control Plane | High CPU starved mutating webhook pods, blocking ReplicaSet creation. |
| **INC-23** | `SEV-2` | Terraform Undeclared Resource Reference on Partial Cleanup | Terraform Monorepo | Deleted cloud resource left orphaned references in security and outputs. |
| **INC-24** | `SEV-2` | Entra ID OIDC Subject Mismatch on Environment Name | GitHub Actions WIF | OIDC assertion subject omitted `-prod` environment suffix. |
| **INC-25** | `SEV-2` | React JSX Sibling Expression Parsing Failure in Assistant Header | Frontend Build Engine | Sibling JSX elements lacked enclosing fragment; loop variable undefined. |
| **INC-26** | `SEV-2` | Bash Inline Script Syntax Error on Nested Loop in GitHub Actions | CI/CD Runner Engine | Inline recovery shell script lacked matching `done` terminator. |

---

## 3. Exhaustive Incident Post-Mortems & Root Cause Analyses

---

### INC-01: GitHub Actions Dynamic Matrix Parse Failure (`matrix` context)
* **Severity:** `SEV-2 (High)` | **Subsystem:** `.github/workflows/terraform-drift-detection.yml`

#### 1. Symptom & Failure Log:
```text
2026-08-23T09:49:34.123Z ##[error]Unrecognized named-value: 'matrix' @[c:\...\terraform-drift-detection.yml:L43]
2026-08-23T09:49:34.124Z ##[error]Workflow syntax validation failed. Pipeline aborted before starting.
```

#### 2. 5-Whys Root Cause Analysis:
1. **Why did the workflow fail?** The workflow parser threw an unrecognized named-value syntax error on line 43.
2. **Why was `matrix` unrecognized?** The condition `if: ${{ matrix.root == inputs.target_root }}` was placed at the job root (`jobs.detect-drift.if`).
3. **Why is `matrix` invalid at job root?** GitHub Actions evaluates job-level `if:` conditions during pipeline compilation *before* `strategy.matrix` is expanded.
4. **Why was it placed there?** The author attempted to filter execution of individual Terraform roots from a single workflow trigger.
5. **Root Cause:** Fundamental misunderstanding of GitHub Actions context lifecycle; `matrix` is only valid inside job steps or `matrix.include`, never in `jobs.<id>.if`.

#### 3. Immediate Code Remediation (Diff):
```diff
- jobs:
-   detect-drift:
-     if: ${{ matrix.root == github.event.inputs.target_root || github.event.inputs.target_root == 'all' }}
-     strategy:
-       matrix:
-         root: [platform/bootstrap, platform/hub, ...]
+ jobs:
+   resolve-targets:
+     runs-on: ubuntu-latest
+     outputs:
+       matrix: ${{ steps.set-matrix.outputs.matrix }}
+     steps:
+       - id: set-matrix
+         run: |
+           SELECTED=$(echo "$ALL_TARGETS" | jq -c --arg target "$TARGET" '[.[] | select(.root == $target)]')
+           echo "matrix=$SELECTED" >> $GITHUB_OUTPUT
+   detect-drift:
+     needs: resolve-targets
+     strategy:
+       matrix:
+         include: ${{ fromJson(needs.resolve-targets.outputs.matrix) }}
```

---

### INC-02: Runner Output Corruption via Multiline `$GITHUB_OUTPUT`
* **Severity:** `SEV-2 (High)` | **Subsystem:** GitHub Actions Runner Environment

#### 1. Symptom & Failure Log:
```text
2026-08-23T10:12:47.489Z ##[error]Unable to process file command 'output' successfully.
2026-08-23T10:12:47.490Z ##[error]Invalid format '  {"name":"Platform - Bootstrap","root":"platform/bootstrap"}'
```

#### 2. Root Cause:
Output string written to `$GITHUB_OUTPUT` contained unescaped raw newlines without using EOF delimiter syntax. GitHub Actions environment file protocol requires single-line `name=value` pairs.

#### 3. Immediate Code Remediation:
```bash
# Broken (Multiline raw echo):
echo "matrix=$ALL_TARGETS" >> $GITHUB_OUTPUT

# Option A (Compact single-line JSON):
ALL_TARGETS='[{"name":"Platform - Bootstrap","root":"platform/bootstrap",...}]'
echo "matrix=$ALL_TARGETS" >> $GITHUB_OUTPUT

# Option B (EOF Delimiter Syntax):
echo "matrix<<EOF" >> $GITHUB_OUTPUT
echo "$ALL_TARGETS" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT
```

---

### INC-03: Dynamic Bracket Dereferencing on Secrets Context
* **Severity:** `SEV-2 (High)` | **Subsystem:** GitHub Actions Security / WIF

#### 1. Symptom & Failure Log:
```text
Run azure/login@v2
  client-id: ''
  tenant-id: '4cef0d84-84d6-4ed0-8abe-773b015bcf99'
##[error]Missing required input: client-id. Azure Login failed.
```

#### 2. Root Cause:
Expression `client-id: ${{ secrets[matrix.secret_name] }}` evaluated to empty string. GitHub Actions security architecture intentionally prohibits dynamic runtime bracket indexing on the `secrets` object.

#### 3. Resolution:
Pass public Entra ID Client IDs directly inside matrix objects (`client_id: '934ab83b-...'`) since Application IDs are public identifiers, while keeping OIDC secrets strictly managed by Entra ID.

---

### INC-04: Multi-Agent Semantic Drift & Hallucination Loop on Off-Topic Queries
* **Severity:** `SEV-2 (High)` | **Subsystem:** Multi-Agent Orchestrator / LangGraph State

#### 1. Symptom:
When a user submitted the off-topic prompt `"how to fly in sky"`, the copilot took 14.5 seconds and generated a detailed 3-paragraph answer explaining NRI KYC Video Customer Identification Process (V-CIP).

#### 2. Root Cause:
Iteration 1 for `"how to fly in sky"` returned 0 vector hits from Qdrant. The reflection loop assumed the search query was simply malformed and injected synthetic feedback `"Search for RBI Master Direction on kyc"`, pulling unrelated documents into context and forcing synthesis.

#### 3. Resolution:
Enforced mathematical vector centroid sieve and deterministic out-of-scope guardrail in `SupervisorAgent` checking raw prompt before vector retrieval to terminate off-topic queries in < 5ms.

---

### INC-05: Embedded Grafana Mixed Content & Zero-Egress Security
* **Severity:** `SEV-3 (Medium)` | **Subsystem:** Frontend UI / AKS Ingress

#### 1. Symptom:
On `https://bank.mytaxbot.site`, clicking the "Live Embedded Grafana" tab showed a blank box: `Mixed Content: The page at 'https://...' was loaded over HTTPS, but requested an insecure frame 'http://localhost:3000'`.

#### 2. Root Cause:
Web browsers block embedding insecure HTTP frames inside secure HTTPS origins. Furthermore, exposing Grafana with a Public IP would incur extra egress bandwidth costs and expand the perimeter attack surface.

#### 3. Resolution:
Render native React real-time telemetry panels on the website. Keep Grafana as internal `ClusterIP` in the `monitoring` namespace, accessed securely via `kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring`.

---

### INC-06: Oryx/Vite Build Failure via UTF-8 Byte Order Mark (BOM)
* **Severity:** `SEV-2 (High)` | **Subsystem:** Azure Static Web Apps Build Engine

#### 1. Symptom:
`[Failed to load PostCSS config: [SyntaxError] Unexpected token ' ', " { "name"... is not valid JSON`.

#### 2. Root Cause:
Editing JSON/CSS configuration files in Windows Notepad saved the file with an invisible UTF-8 Byte Order Mark (`\uFEFF`) at index 0. Node's `JSON.parse` failed when reading raw strings starting with byte 0 `\uFEFF`.

#### 3. Resolution:
Stripped BOM markers across all files using UTF-8 without BOM encoding (`New-Object System.Text.UTF8Encoding($false)`).

---

### INC-07: Azure OpenAI API Version vs Reasoning Parameter (`max_completion_tokens`)
* **Severity:** `SEV-2 (High)` | **Subsystem:** LiteLLM / Azure OpenAI Service

#### 1. Symptom:
`litellm.exceptions.BadRequestError: Azure OpenAI error: 400 - 'max_tokens' is not supported on reasoning models. Use 'max_completion_tokens' instead.`

#### 2. Root Cause:
When upgrading deployments from standard GPT-4 to newer reasoning models (`gpt-5.4-nano` / OpenAI o-series), the API schema deprecated `max_tokens` in favor of `max_completion_tokens`.

#### 3. Resolution:
Updated LiteLLM gateway parameter mappings and pinned API version to `2024-06-01`.

---

### INC-08: AKS Pod Stale Image Caching on Mutable Container Tags (`:latest`)
* **Severity:** `SEV-2 (High)` | **Subsystem:** Kubernetes Pod Lifecycle

#### 1. Symptom:
A new backend commit was pushed and deployed, but AKS pods continued serving the previous version of the code.

#### 2. Root Cause:
The deployment manifest specified `imagePullPolicy: IfNotPresent` with image tag `:latest`. The kubelet skipped pulling updated layers because `:latest` was already cached.

#### 3. Resolution:
Tagged images with explicit Git commit SHAs (`image: ghcr.io/.../backend:sha-a1b2c3d`) and set `imagePullPolicy: Always` in Kubernetes manifests.

---

### INC-09: APIM Gateway CORS Preflight Failure on Custom Headers
* **Severity:** `SEV-2 (High)` | **Subsystem:** Azure API Management (APIM)

#### 1. Symptom:
Browser console: `Access to fetch at 'https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1/compliance/query' has been blocked by CORS policy: Request header field x-session-id is not allowed by Access-Control-Allow-Headers`.

#### 2. Root Cause:
The React frontend sent custom telemetry headers (`x-session-id`, `x-request-source`) which were not explicitly permitted in the APIM inbound XML policy.

#### 3. Resolution:
Updated APIM inbound policy to allow wildcard headers (`<header>*</header>`) inside the `<cors>` policy block.

---

### INC-10: Terraform Backend Partial Configuration Error
* **Severity:** `SEV-2 (High)` | **Subsystem:** Terraform IaC Pipeline

#### 1. Symptom:
`Error: Backend configuration changed. Run "terraform init" with the "-reconfigure" flag.`

#### 2. Root Cause:
Monorepo uses partial backend definitions with empty `backend "azurerm" {}` in `versions.tf`.

#### 3. Resolution:
Always initialize Terraform with: `terraform init -reconfigure -backend-config=backend.hcl -input=false`.

---

### INC-11: Qdrant Persistent Volume Permission Lock on Node Rescheduling
* **Severity:** `SEV-2 (High)` | **Subsystem:** AKS CSI Storage / Qdrant

#### 1. Symptom:
Qdrant pod entered `CrashLoopBackOff`: `Storage directory /qdrant/data is locked by another process (OS error 11: Resource temporarily unavailable)`.

#### 2. Root Cause:
When AKS rescheduled the pod to a different worker node, Azure Managed Disk detachment from the old node experienced a 60-second storage attachment lock.

#### 3. Resolution:
Updated `StatefulSet` with `readinessProbe` and `terminationGracePeriodSeconds: 30` to guarantee clean storage volume unmounting before pod termination.

---

### INC-12: DPDP Act PII Sanitizer Catastrophic Regex Backtracking
* **Severity:** `SEV-3 (Medium)` | **Subsystem:** `pii_shield.py`

#### 1. Symptom:
FastAPI backend CPU spiked to 100% and timed out when evaluating large regulatory documents containing complex nested strings.

#### 2. Root Cause:
The PAN redaction regex contained nested greedy quantifiers (`([A-Z]{5}[0-9]{4}[A-Z]{1})+`), triggering exponential regex backtracking.

#### 3. Resolution:
Refactored regex patterns to use atomic, non-backtracking character classes (`r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'`).

---

### INC-13: Static Web App Deployment Token Misalignment
* **Severity:** `SEV-2 (High)` | **Subsystem:** `app-deploy-swa.yml` / GitHub Actions

#### 1. Symptom:
`Azure/static-web-apps-deploy@v1` fails with HTTP 400 `BadRequest: No matching Static Web App was found or the api key was invalid`.

#### 2. Root Cause:
In caller workflows calling reusable `app-deploy-swa.yml`, `swa_token_secret_name` was omitted and defaulted to a legacy uppercase secret name (`SWA-TAXB-DEPLOYMENT-TOKEN`) containing an obsolete token, whereas Terraform stores the live API key in `taxb-swa-deployment-token`.

#### 3. Resolution:
Explicitly pass `swa_token_secret_name: 'taxb-swa-deployment-token'` in the caller workflow `with:` block and ensure Key Vault secrets reflect the live `az staticwebapp secrets list` API token.

---

### INC-14: AKS Ingress Public IP Elimination via Internal Web App Routing
* **Severity:** `SEV-3 (Medium)` | **Subsystem:** AKS Networking / Ingress Controller

#### 1. Symptom:
AKS Web App Routing addon provisioned an unwanted public IP (`kubernetes-*`) on the NGINX ingress controller incurring hourly static IP charges (~$3.65/mo).

#### 2. Root Cause:
By default, AKS Web App Routing initializes NGINX with `defaultIngressControllerType: External` creating a public Azure Load Balancer frontend.

#### 3. Resolution:
Reconfigured App Routing to internal mode via Azure CLI (`az aks approuting update --nginx Internal --name <cluster> --resource-group <rg>`) or set `loadBalancerAnnotations: { "service.beta.kubernetes.io/azure-load-balancer-internal": "true" }` on the `NginxIngressController` CRD.

---

### INC-15: GHA Workflow UI Disconnect on Feature Branch Rename
* **Severity:** `SEV-3 (Medium)` | **Subsystem:** GitHub Actions UI / Dispatch

#### 1. Symptom:
In GitHub Actions UI, clicking **Run workflow** displays yellow warning: `Workflow does not exist or does not have a workflow_dispatch trigger in this branch` with the button disabled.

#### 2. Root Cause:
GitHub Actions UI caches the historical YAML filename (`terraform-unified-manager.yml`). When the file was renamed in a feature branch, GitHub failed to match the historical filename.

#### 3. Resolution:
Ensure the exact YAML filename expected by the UI (`terraform-unified-manager.yml`) exists in the branch with a valid `workflow_dispatch:` trigger.

---

### INC-16: Reusable Workflow Permission Delegation Failure
* **Severity:** `SEV-2 (High)` | **Subsystem:** GitHub Actions Security / Reusable Templates

#### 1. Symptom:
Workflow failure on startup: `Error calling workflow '.../reusable-checkov-scan.yml...'. The workflow is requesting 'actions: read', but is only allowed 'actions: none'`.

#### 2. Root Cause:
When a caller workflow defines an explicit top-level `permissions:` block, any undeclared scopes default to `none`. GitHub Actions enforces that a called reusable workflow's requested permissions must be a subset of what the caller grants. `github/codeql-action/upload-sarif` requires `actions: read` along with `security-events: write` and `contents: read`.

#### 3. Resolution:
Explicitly include `actions: read` in the caller workflow's top-level `permissions:` block alongside `contents: read`, `security-events: write`, and `id-token: write`.

---

### INC-17: 3-Layer Mathematical Vector Centroid Guardrail Interception
* **Severity:** `SEV-2 (High)` | **Subsystem:** AI Safety / Multi-Agent Guardrails

#### 1. Symptom:
Adversarial or random off-topic prompts (e.g. `"why my bathroom running without water"`, `"how to fly in sky"`, `"i want to fry"`) bypassed domain guardrails when conversational history was present or when prompts started with common question words (`why`, `who`, `what if`).

#### 2. Root Cause:
Handcrafted regex lists (`FOLLOWUP_PATTERNS`, `DOMAIN_KEYWORDS`) and string concatenation (`old_q + " -> " + new_q`) are brittle heuristics that fail on natural linguistic variations.

#### 3. Resolution:
Replaced all regex heuristics with **Layer 1 Mathematical Vector Centroid Sieve** (cosine distance < 3ms in-memory) in `DomainCentroidGuardrail` and **Layer 2 LLM Intent Disambiguation** without context string-stitching.

---

### INC-18: LiteLLM Routing Strategy Enterprise License Exception
* **Severity:** `SEV-2 (High)` | **Subsystem:** LiteLLM AI Gateway / Helm Chart

#### 1. Symptom:
`litellm-proxy` pod goes into `CrashLoopBackOff` with exit code 3. Helm upgrade times out with `Error: context deadline exceeded`. Logs show `Exception: You must be a LiteLLM Enterprise user to use this feature. If you have a license please set LITELLM_LICENSE in your env.`

#### 2. Root Cause:
`router_settings.routing_strategy: "latency-based-routing"` is an enterprise-only feature in LiteLLM. When deployed in open-source LiteLLM without `LITELLM_LICENSE`, the proxy aborts startup immediately.

#### 3. Resolution:
Set `routing_strategy: "least-busy"` or `"simple-shuffle"` in `litellm-configmap.yaml` and `k8s/litellm/config.yaml`. These strategies are 100% free and open-source.

---

### INC-19: Domain Guardrail False Positives on Colloquial Banking Phrasing
* **Severity:** `SEV-2 (High)` | **Subsystem:** AI Safety / Centroid Guardrail

#### 1. Symptom:
User questions regarding loan recovery, Fair Practices Code, and collection practices (e.g. `"how to collect lending money"`) were falsely intercepted with `Out of Regulatory Scope` / `governance-abstention-shield`.

#### 2. Root Cause:
The in-memory vector centroid was initialized against only 6 baseline circulars without stopword filtering. Common question words diluted sparse vectors, while colloquial loan collection terms (`collect`, `money`, `debts`) fell just below the static cosine threshold.

#### 3. Resolution:
Implemented stopword-filtered tokenization in `domain_guardrail.py`, auto-indexed all 12+ Master Directions, and calibrated mathematical thresholds (`DOMAIN_SIMILARITY_THRESHOLD = 0.030`, `MAX_CLAUSE_SIMILARITY_THRESHOLD = 0.060`).

---

### INC-20: Azure Cognitive Services Soft-Delete Name Collision
* **Severity:** `SEV-2 (High)` | **Subsystem:** Terraform / Azure Resource Manager

#### 1. Symptom:
`azapi_resource` creation for Azure OpenAI or Content Safety fails with `409 Conflict: FlagMustBeSetForRestore` ("An existing resource with ID '...' has been soft-deleted. To restore it, set the restore flag to true").

#### 2. Root Cause:
Deleting an Azure Cognitive Services account places it into a soft-deleted retention state (48 hours to 90 days). ARM resource creation requests (`PUT`) fail because the resource name remains locked in the subscription recycle bin.

#### 3. Resolution:
Purged the soft-deleted resource from the recycle bin before re-running Terraform apply:
```bash
az cognitiveservices account purge --name <account-name> --resource-group <rg-name> --location <location> --subscription <sub-id>
```

---

### INC-21: Azure Storage Authorization 403 on Entra ID Blob Sync
* **Severity:** `SEV-2 (High)` | **Subsystem:** Storage Data Plane / Entra ID WIF

#### 1. Symptom:
`azcopy sync` or `az storage blob sync` using Azure AD authentication fails with `403 This request is not authorized to perform this operation using this permission. ERROR CODE: AuthorizationPermissionMismatch`.

#### 2. Root Cause:
Standard ARM control-plane roles (`Contributor`, `Owner`) do NOT grant data-plane access to blob containers. When authenticating via Entra ID (WIF OIDC Service Principal), Azure Storage enforces explicit data plane RBAC.

#### 3. Resolution:
Assigned the `Storage Blob Data Contributor` role to the Deployment Service Principal (`app-prod` Object ID: `9630f661-27e7-42f0-8377-5565ba7db7cd`) on the target storage account (`sthttaxbpcin01`) and declared `azurerm_role_assignment.cicd_blob_contributor` in `workloads/tax-advisor/security_rbac.tf`.

---

### INC-22: Helm Upgrade Timeout on AKS Workload Identity Webhook Deadlock
* **Severity:** `SEV-1 (Critical)` | **Subsystem:** AKS Control Plane / Mutating Webhooks

#### 1. Symptom:
`helm upgrade --install` times out after 10m with `Error: UPGRADE FAILED: context deadline exceeded`. `kubectl describe rs` shows `Error creating: Internal error occurred: failed calling webhook "mutation.azure-workload-identity.io": no endpoints available for service "azure-wi-webhook-webhook-service"`.

#### 2. Root Cause:
When an AKS single-node cluster reaches 99% CPU request capacity, the `azure-wi-webhook-controller-manager` pod in `kube-system` goes into `Pending (Insufficient cpu)`. Any application pod labeled with `azure.workload.identity/use: "true"` invokes this mutating webhook on creation, causing ReplicaSet creation to fail and Helm rolling updates to time out.

#### 3. Resolution:
For workloads using direct API keys passed via Kubernetes Secrets (like LiteLLM proxy and backend with multi-cloud secrets), removed `azure.workload.identity/use: "true"` from pod templates. Cleaned up failed Helm release secrets: `kubectl delete secret -l owner=helm,name=bank-compliance,status=failed -n bank-compliance`.

---

### INC-23: Terraform Undeclared Resource Reference on Partial Cleanup
* **Severity:** `SEV-2 (High)` | **Subsystem:** Terraform Monorepo / Governance

#### 1. Symptom:
`terraform validate` or CI/CD Plan pipeline fails with `Error: Reference to undeclared resource ... on security.tf ... on outputs.tf ... A managed resource "azurerm_search_service" "shared_ai_search" has not been declared in the root module`.

#### 2. Root Cause:
When deprecating or removing an unused Azure cloud resource from its definition file (`ai_services.tf`), downstream references in `security.tf` (Key Vault secrets, RBAC role assignments) and `outputs.tf` were not simultaneously removed.

#### 3. Resolution:
Cleaned up all downstream consumers of the deleted resource: removed orphaned `azurerm_key_vault_secret`, `azurerm_role_assignment`, and `output` blocks. Enforced running `terraform validate` across all root modules before pushing to git.

---

### INC-24: Entra ID OIDC Subject Mismatch on Environment Name
* **Severity:** `SEV-2 (High)` | **Subsystem:** GitHub Actions WIF / Entra ID

#### 1. Symptom:
Workflow fails at `azure/login@v2` step with `AADSTS700213: No matching federated identity record found for presented assertion subject 'repo:RepoCodeGanesh/terraform-azure-iac:environment:<env-name>'. Check your federated identity credential Subject, Audience and Issuer against the presented assertion`.

#### 2. Root Cause:
In GitHub Actions workflows calling reusable templates (`tf-plan.yml` / `tf-apply.yml`), `environment_name:` was configured with an un-suffixed name (e.g. `'bootstrap'` instead of `'bootstrap-prod'`). Entra ID App Registrations are configured with explicit Federated Identity Credentials expecting exact subject claims matching `repo:RepoCodeGanesh/terraform-azure-iac:environment:<root>-prod`.

#### 3. Resolution:
Synchronized `environment_name` in caller workflows to match the exact `-prod` environment configured on the corresponding Entra ID App Registration (`bootstrap-prod`, `hub-prod`, `shared-services-prod`, `bank-compliance-prod`, `tax-advisor-prod`).

---

### INC-25: React JSX Sibling Expression Parsing Failure in Assistant Header
* **Severity:** `SEV-2 (High)` | **Subsystem:** Frontend Build Engine / Vite SPA

#### 1. Symptom:
Vite SPA production build fails with `[vite:esbuild] Transform failed with 1 error: ... ChatWindow.jsx:245:16: ERROR: Expected ")" but found "{"`.

#### 2. Root Cause:
Inside a conditional expression `{m.role === 'assistant' && ( ... )}`, multiple sibling elements (the telemetry badge bar and the expandable trace block) were placed consecutively without an enclosing React Fragment (`<> ... </>`). Additionally, loop iterator indexing used an undefined variable `i` instead of map parameter `idx`.

#### 3. Resolution:
Wrapped all sibling elements within a React Fragment (`<> ... </>`) inside the conditional expression and used `idx` consistently for trace toggling state.

---

### INC-26: Bash Inline Script Syntax Error on Nested Loop in GitHub Actions
* **Severity:** `SEV-2 (High)` | **Subsystem:** CI/CD Runner Engine / Bash Script

#### 1. Symptom:
GitHub Actions deployment step terminates with `/home/runner/work/...sh: line 80: syntax error: unexpected end of file` (exit code 2).

#### 2. Root Cause:
In the inline bash script for auto-recovering stuck Helm releases, an outer loop `for STUCK_STATUS in ...; do` was opened but lacked a closing `done` before proceeding to the FinOps quota scaling block.

#### 3. Resolution:
Ensured all `for` loops in CI/CD inline shell scripts have corresponding `done` terminators. Always match `do ... done` pairs before adding downstream execution stages.
