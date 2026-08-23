# Confluence Technical Knowledge Base: Master Incident Post-Mortems & Root Cause Analysis (RCA)

**Document ID:** `CR-SRE-10`  
**Classification:** Enterprise SRE, DevOps & AI Platform Post-Mortems  
**Target Environment:** HappyTechies Enterprise Landing Zone & GenAIOps Applications  
**Status:** `LIVING KNOWLEDGE BASE / AUDITED`  

---

## 1. SRE Incident Severity Classification Framework

All platform incidents are triaged and documented using standard SRE severity tiers:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                INCIDENT SEVERITY MATRIX                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
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

---

## 3. Exhaustive Incident Post-Mortems & Root Cause Analyses

---

### INC-01: GitHub Actions Job-Level Matrix Context Evaluation Failure
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
+           # Dynamically filter matrix array via jq and emit to outputs
+           SELECTED=$(echo "$ALL_TARGETS" | jq -c --arg target "$TARGET" '[.[] | select(.root == $target)]')
+           echo "matrix=$SELECTED" >> $GITHUB_OUTPUT
+   detect-drift:
+     needs: resolve-targets
+     strategy:
+       matrix:
+         include: ${{ fromJson(needs.resolve-targets.outputs.matrix) }}
```

#### 4. Permanent Prevention:
* Enforce dynamic matrix pre-resolution jobs (`resolve-targets`) whenever matrix filtering is needed.

---

### INC-02: Runner Output Corruption via Multiline `$GITHUB_OUTPUT`
* **Severity:** `SEV-2 (High)` | **Subsystem:** GitHub Actions Runner Environment

#### 1. Symptom & Failure Log:
```text
2026-08-23T10:12:47.489Z ##[error]Unable to process file command 'output' successfully.
2026-08-23T10:12:47.490Z ##[error]Invalid format '  {"name":"Platform - Bootstrap","root":"platform/bootstrap"}'
```

#### 2. 5-Whys Root Cause Analysis:
1. **Why did the runner fail?** The runner failed processing the `$GITHUB_OUTPUT` environment file.
2. **Why was format invalid?** The string written to `$GITHUB_OUTPUT` spanned multiple lines with raw unescaped newlines.
3. **Why did newlines break it?** GitHub Actions environment file protocol requires single-line `name=value` pairs.
4. **Why was it multiline?** The shell variable `ALL_TARGETS='[\n  {...}\n]'` was echoed directly: `echo "matrix=$ALL_TARGETS" >> $GITHUB_OUTPUT`.
5. **Root Cause:** Output string contained unescaped newlines without using EOF delimiter syntax.

#### 3. Immediate Code Remediation:
```bash
# ❌ Broken (Multiline raw echo):
echo "matrix=$ALL_TARGETS" >> $GITHUB_OUTPUT

# ✅ Option A (Compact single-line JSON):
ALL_TARGETS='[{"name":"Platform - Bootstrap","root":"platform/bootstrap",...}]'
echo "matrix=$ALL_TARGETS" >> $GITHUB_OUTPUT

# ✅ Option B (EOF Delimiter Syntax):
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
* Expression `client-id: ${{ secrets[matrix.secret_name] }}` evaluated to empty string.
* GitHub Actions security architecture intentionally prohibits dynamic runtime bracket indexing on the `secrets` object to prevent token leakage via index enumeration.

#### 3. Resolution:
* Pass public Entra ID Client IDs directly inside matrix objects (`client_id: '934ab83b-...'`) since Application IDs are public identifiers, while keeping OIDC secrets strictly managed by Entra ID.

---

### INC-04: Multi-Agent Semantic Drift & Hallucination Loop on Off-Topic Queries
* **Severity:** `SEV-2 (High)` | **Subsystem:** Multi-Agent Orchestrator / LangGraph State

#### 1. Symptom:
* When a user submitted the off-topic prompt `"how to fly in sky"`, the copilot took **14.5 seconds** and generated a detailed 3-paragraph answer explaining **NRI KYC Video Customer Identification Process (V-CIP)**.

#### 2. 5-Whys Root Cause Analysis:
1. **Why did the copilot hallucinate NRI KYC?** The Synthesizer Agent received NRI KYC clauses in its prompt context and synthesized an answer.
2. **Why were NRI KYC clauses in context?** The Retriever Agent returned those clauses during iteration 2.
3. **Why did iteration 2 retrieve KYC clauses?** The Auditor Agent injected synthetic feedback: `"Search for RBI Master Direction on kyc"`.
4. **Why did the Auditor inject KYC feedback?** Iteration 1 for `"how to fly in sky"` returned 0 vector hits from Qdrant. The reflection loop assumed the search query was simply malformed and defaulted to a generic banking search.
5. **Root Cause:** Absence of a deterministic domain relevance check before entering the vector retrieval and reflection loops.

#### 3. Immediate Code Remediation (Diff in `supervisor_agent.py`):
```diff
+ # Enforce deterministic domain guardrail BEFORE vector retrieval
+ query_lower = state["sanitized_query"].lower()
+ banking_keywords = ["rbi", "kyc", "bank", "account", "loan", "card", "ciso", "cloud", "audit"]
+ is_banking = any(k in query_lower for k in banking_keywords)
+
+ if not is_banking and len(query_lower.split()) > 2:
+     state["intent"] = "out_of_scope"
+     return state  # Terminates state machine in < 10ms with zero token cost
```

---

### INC-05: Embedded Grafana Mixed Content & Zero-Egress Security
* **Severity:** `SEV-3 (Medium)` | **Subsystem:** Frontend UI / AKS Ingress

#### 1. Symptom:
* On `https://bank.mytaxbot.site`, clicking the "Live Embedded Grafana" tab showed a blank box or browser security warning: `Mixed Content: The page at 'https://...' was loaded over HTTPS, but requested an insecure frame 'http://localhost:3000'`.

#### 2. Root Cause:
* Web browsers enforce strict Mixed Content / Content Security Policy (CSP) blocking insecure HTTP frames inside secure HTTPS origins.
* Furthermore, exposing Grafana with a Public IP would incur extra egress bandwidth costs and expand the perimeter attack surface.

#### 3. Resolution:
* Render **native React real-time telemetry panels** on the website consuming sanitized stats from `/api/v1/compliance/stats`.
* Isolate Grafana as internal `ClusterIP` in the `monitoring` namespace, accessed securely by engineers via:
  ```bash
  kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
  ```

---

### INC-06: Oryx/Vite Build Failure via UTF-8 Byte Order Mark (BOM)
* **Severity:** `SEV-2 (High)` | **Subsystem:** Azure Static Web Apps Build Engine

#### 1. Symptom:
```text
[Failed to load PostCSS config: [SyntaxError] Unexpected token ' ', " { "name"... is not valid JSON
```

#### 2. Root Cause:
* Editing JSON/CSS configuration files in Windows Notepad saved the file with an invisible **UTF-8 Byte Order Mark (BOM: `\uFEFF`)** at index 0.
* Standard Linux build tools (Oryx, PostCSS, Vite) expect pure ASCII/UTF-8 without BOM, causing JSON parse failure on character 1.

#### 3. Resolution:
* Stripped BOM markers using PowerShell:
  ```powershell
  $content = Get-Content package.json -Raw
  [System.IO.File]::WriteAllText("package.json", $content, (New-Object System.Text.UTF8Encoding($false)))
  ```

---

### INC-07: Azure OpenAI API Version vs Reasoning Parameter (`max_completion_tokens`)
* **Severity:** `SEV-2 (High)` | **Subsystem:** LiteLLM / Azure OpenAI Service

#### 1. Symptom:
```text
litellm.exceptions.BadRequestError: Azure OpenAI error: 400 - 'max_tokens' is not supported on reasoning models. Use 'max_completion_tokens' instead.
```

#### 2. Root Cause:
* When upgrading deployments from standard GPT-4 to newer reasoning models (such as `gpt-5.4-nano` / OpenAI o-series), the API schema deprecated `max_tokens` in favor of `max_completion_tokens`.

#### 3. Resolution:
* Upgraded LiteLLM gateway parameter mappings in `orchestrator.py` and pinned API version to `2024-06-01`.

---

### INC-08: AKS Pod Stale Image Caching on Mutable `:latest` Tag
* **Severity:** `SEV-2 (High)` | **Subsystem:** Kubernetes Pod Lifecycle

#### 1. Symptom:
* A new backend commit was pushed and deployed, but AKS pods continued serving the previous version of the code.

#### 2. Root Cause:
* The deployment manifest specified `imagePullPolicy: IfNotPresent` with image tag `:latest`. Since a container tagged `:latest` already existed on the AKS worker node, the kubelet skipped pulling the updated image layers from GHCR.

#### 3. Resolution:
* Tagged images with explicit Git commit SHAs (`image: ghcr.io/.../backend:sha-a1b2c3d`) and set `imagePullPolicy: Always` in Kubernetes manifests.

---

### INC-09: APIM Gateway CORS Preflight Failure on Custom Headers
* **Severity:** `SEV-2 (High)` | **Subsystem:** Azure API Management (APIM)

#### 1. Symptom:
* Browser console reported: `Access to fetch at 'https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1/compliance/query' has been blocked by CORS policy: Request header field x-session-id is not allowed by Access-Control-Allow-Headers`.

#### 2. Root Cause:
* The React frontend sent custom telemetry headers (`x-session-id`, `x-request-source`) which were not explicitly permitted in the APIM inbound XML policy.

#### 3. Resolution:
* Updated APIM inbound policy to allow wildcard headers (`<header>*</header>`) inside the `<cors>` policy block.

---

### INC-10: Terraform Backend Partial Configuration Error
* **Severity:** `SEV-2 (High)` | **Subsystem:** Terraform IaC Pipeline

#### 1. Symptom:
```text
Error: Backend configuration changed. Run "terraform init" with the "-reconfigure" flag.
```

#### 2. Root Cause:
* Monorepo uses partial backend definitions with empty `backend "azurerm" {}` in `versions.tf`. When switching branches or runner environments, cached state metadata conflicted with the new backend configuration.

#### 3. Resolution:
* Standardized all CI/CD pipelines and developer scripts to execute:
  ```bash
  terraform init -reconfigure -backend-config=backend.hcl -input=false
  ```

---

### INC-11: Qdrant Persistent Volume Permission Lock on Node Rescheduling
* **Severity:** `SEV-2 (High)` | **Subsystem:** AKS CSI Storage / Qdrant

#### 1. Symptom:
* Qdrant pod entered `CrashLoopBackOff` with error: `Storage directory /qdrant/data is locked by another process (OS error 11: Resource temporarily unavailable)`.

#### 2. Root Cause:
* When AKS rescheduled the pod to a different worker node, Azure Managed Disk detachment from the old node experienced a 60-second storage attachment lock.

#### 3. Resolution:
* Updated `StatefulSet` with `readinessProbe` and `terminationGracePeriodSeconds: 30` to guarantee clean storage volume unmounting before pod termination.

---

### INC-12: DPDP Act PII Sanitizer Catastrophic Regex Backtracking
* **Severity:** `SEV-3 (Medium)` | **Subsystem:** `pii_shield.py`

#### 1. Symptom:
* FastAPI backend CPU spiked to 100% and timed out when evaluating large regulatory documents containing complex nested strings.

#### 2. Root Cause:
* The PAN redaction regex contained nested greedy quantifiers (`([A-Z]{5}[0-9]{4}[A-Z]{1})+`), triggering exponential regex backtracking on malicious or malformed inputs.

#### 3. Resolution:
* Refactored regex patterns to use atomic, non-backtracking character classes:
  ```python
  PAN_REGEX = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
  AADHAAR_REGEX = re.compile(r'\b[2-9][0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b')
  ```
