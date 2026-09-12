# 11. BankCompliance AI: Engineering Learnings & Troubleshooting

* **Space:** `HappyTechies Cloud & AI Platform` -> `Runbooks & Masterclasses`
* **Live Domain:** [https://bank.mytaxbot.site](https://bank.mytaxbot.site)
* **APIM Gateway:** `https://apim-ht-ss-p-cin-01.azure-api.net/bankc`
* **Status:** `PRODUCTION READY & FULLY AUTOMATED`

---

## Table of Contents
1. [Architecture Overview & Flow](#1-architecture-overview--flow)
2. [Detailed Issue Breakdown & Resolutions](#2-detailed-issue-breakdown--resolutions)
   * [Issue 1: GitHub Actions Dynamic Environment Context vs Step Outputs](#1-github-actions-dynamic-environment-context-vs-step-outputs)
   * [Issue 2: Oryx / Vite Build Breakage via UTF-8 Byte Order Mark (BOM)](#2-oryx--vite-build-breakage-via-utf-8-byte-order-mark-bom)
   * [Issue 3: Frontend Fallback to Localhost & ClusterIP Networking](#3-frontend-fallback-to-localhost--clusterip-networking)
   * [Issue 4: Content Security Policy (CSP) & Browser Mixed Content Restrictions](#4-content-security-policy-csp--browser-mixed-content-restrictions)
   * [Issue 5: Azure OpenAI API Version vs Model Release Version](#5-azure-openai-api-version-vs-model-release-version)
   * [Issue 6: Reasoning Model Parameters (`max_tokens` vs `max_completion_tokens`)](#6-reasoning-model-parameters-max_tokens-vs-max_completion_tokens)
   * [Issue 7: Kubernetes Image Caching (`imagePullPolicy` & Commit SHA Tagging)](#7-kubernetes-image-caching-imagepullpolicy--commit-sha-tagging)
   * [Issue 8: Semantic PR Title Validation Failure (`action-semantic-pull-request`)](#8-semantic-pr-title-validation-failure-action-semantic-pull-request)
   * [Issue 9: Modern Azure OpenAI Parameter Compatibility](#9-modern-azure-openai-parameter-compatibility)
   * [Issue 10: Heterogeneous Multi-Agent AI Routing (Google Gemini + Azure OpenAI)](#10-heterogeneous-multi-agent-ai-routing-google-gemini--azure-openai)
   * [Issue 11: Out-of-Scope Reflection Loop Prevention (Governance Abstention Shield)](#11-out-of-scope-reflection-loop-prevention-governance-abstention-shield)
   * [Issue 12: GenAIOps Grafana Command Center & Zero-Baseline Metric Handling](#12-genaiops-grafana-command-center--zero-baseline-metric-handling)
3. [Platform Engineer Checklist & Golden Rules](#3-platform-engineer-checklist--golden-rules)

---

## 1. Architecture Overview & Flow

```text
+--------------------+       +---------------------------------------------+
|    User Browser    | ----> |           Azure Shared Services             |
| bank.mytaxbot.site | HTTPS | APIM Gateway: apim-ht-ss-p-cin-01           |
+--------------------+       +----------------------+----------------------+
                                                    | Forward to AKS
                                                    v
                             +---------------------------------------------+
                             |           Apps-prod AKS (Central India)     |
                             | Service: bankc-backend-svc (LoadBalancer:80)|
                             | Pod: FastAPI Backend (Port 8000)            |
                             | Pod: LiteLLM Gateway (Port 4000)            |
                             | Pod: Qdrant Vector DB (4GB CSI Managed Disk)|
                             +----------------------+----------------------+
                                                    | Chat Completion
                                                    v
                             +---------------------------------------------+
                             |   Azure OpenAI (oai-ht-taxb-p-eus-01)       |
                             |   Deployment: gpt-5.4-nano                  |
                             +---------------------------------------------+
```

---

## 2. Detailed Issue Breakdown & Resolutions

### 1. GitHub Actions Dynamic Environment Context vs Step Outputs

#### Symptom:
* GitHub Actions workflow validator warning: `Context access might be invalid: IMAGE_TAG @[L66]`.

#### Root Cause:
* In GitHub Actions, static schema validation parses `${{ env.VARIABLE }}` expressions against statically declared variables in `env:` blocks.
* When variables are dynamically exported during a shell step via `echo "IMAGE_TAG=..." >> $GITHUB_ENV`, the static schema analyzer does not register them into the known compile-time schema, generating a context validation error.

#### Resolution:
Use standard GitHub Actions **Step Outputs** (`$GITHUB_OUTPUT`) with explicit step `id`s instead of polluting the global `env` context:

```yaml
# Before (Static context warning):
- name: Downcase Image Name
  run: |
    echo "IMAGE_TAG=${{ env.REGISTRY }}/$(echo ${{ env.IMAGE_NAME }} | tr '[A-Z]' '[a-z]'):latest" >> $GITHUB_ENV
- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    tags: ${{ env.IMAGE_TAG }}

# After (Strictly typed Step Output):
- name: Downcase Image Name
  id: prep_tag
  run: |
    IMAGE_LOWER=$(echo "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}" | tr '[:upper:]' '[:lower:]')
    echo "image_tag=${IMAGE_LOWER}:latest" >> $GITHUB_OUTPUT
- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    tags: ${{ steps.prep_tag.outputs.image_tag }}
```

---

### 2. Oryx / Vite Build Breakage via UTF-8 Byte Order Mark (BOM)

#### Symptom:
* Azure Static Web Apps build step fails inside Oryx:
  ```text
  [Failed to load PostCSS config: Failed to load PostCSS config: [SyntaxError] Unexpected token ' ', " {
  "name"... is not valid JSON
  ```

#### Root Cause:
* On Windows systems, PowerShell output redirection or editors can save text files as **UTF-8 with BOM** (the 3-byte prefix `0xEF 0xBB 0xBF` / Unicode `\uFEFF`).
* During `vite build`, PostCSS uses `cosmiconfig` / `lilconfig` (`jsonLoader`) to inspect `package.json`. Node's native `JSON.parse(content)` fails when reading raw strings starting with byte 0 `\uFEFF`.

#### Resolution:
Strip the UTF-8 BOM from all configuration and source files:
```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
Get-ChildItem -Recurse -File 'frontend' | ForEach-Object {
    $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $text = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
        [System.IO.File]::WriteAllText($_.FullName, $text, $utf8NoBom)
    }
}
```

---

### 3. Frontend Fallback to Localhost & ClusterIP Networking

#### Symptom:
* Users accessing `https://bank.mytaxbot.site` receive:
  `Unable to connect to BankCompliance AKS backend API. Please ensure the cluster and backend services are active.`

#### Root Cause:
1. `VITE_API_URL` was not supplied during the Static Web App build, so Vite evaluated `import.meta.env.VITE_API_URL || 'http://localhost:8000/...'` and baked `http://localhost:8000` into the bundle.
2. In the user's browser, requests were sent to the user's personal laptop (`localhost`).
3. The Kubernetes backend Service was defined as `type: ClusterIP`, meaning it had no public IP or external routing.

#### Resolution:
1. Changed `backend-deployment.yaml` service to `type: LoadBalancer` with an Azure DNS label:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: bankc-backend
     namespace: bank-compliance
     annotations:
       service.beta.kubernetes.io/azure-dns-label-name: "bankc-api-ht-cin"
   spec:
     type: LoadBalancer
     selector:
       app: bankc-backend
     ports:
       - name: http
         port: 80
         targetPort: 8000
   ```
2. Provided `VITE_API_URL` during CI/CD build:
   ```yaml
   - name: Deploy to Azure Static Web Apps
     uses: Azure/static-web-apps-deploy@v1
     env:
       VITE_API_URL: "https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v1/compliance/query"
   ```

---

### 4. Content Security Policy (CSP) & Browser Mixed Content Restrictions

#### Symptom:
* When accessing `https://bank.mytaxbot.site` (HTTPS), browser console logs `Blocked mixed content` or `Violates Content Security Policy directive`.

#### Root Cause:
1. **Mixed Content:** Browsers strictly prohibit secure HTTPS web pages from executing asynchronous HTTP fetch calls (`https://` -> `http://`).
2. **CSP Restrictions:** `staticwebapp.config.json` had `"Content-Security-Policy": "default-src 'self' https: data: ..."` which blocked all non-HTTPS network requests.

#### Resolution:
Configured the **Azure API Management (APIM)** gateway in Terraform HCL (`workloads/bank-compliance-ai-aks/main.tf`):
```hcl
resource "azapi_resource" "apim_bankc_api" {
  type      = "Microsoft.ApiManagement/service/apis@2022-08-01"
  name      = "bankc-compliance-api"
  parent_id = data.azurerm_api_management.shared.id

  body = {
    properties = {
      displayName          = "BankCompliance AI -- Regulatory Copilot"
      path                 = "bankc"
      protocols            = ["https"]
      serviceUrl           = "http://bankc-api-ht-cin.centralindia.cloudapp.azure.com"
      subscriptionRequired = false
    }
  }
}
```
* APIM terminates SSL with a native Microsoft wildcard certificate (`*.azure-api.net`).
* The browser calls `https://apim-ht-ss-p-cin-01.azure-api.net/bankc/...` securely over HTTPS.
* APIM routes the request to AKS over internal/cloud networking.

---

### 5. Azure OpenAI API Version vs Model Release Version

#### Symptom:
* LiteLLM Proxy logs:
  `litellm.exceptions.APIError: AzureException - Error code: 404 - {'error': {'code': '404', 'message': 'Resource not found'}}`

#### Root Cause:
* In `litellm/config.yaml`, `api_version` was incorrectly set to `"2026-03-17"` (which is the model release version, not Azure OpenAI's REST API specification).
* Azure OpenAI rejected the request because API version `2026-03-17` does not exist on Azure OpenAI's API plane.

#### Resolution:
Updated `config.yaml` to use a supported Azure OpenAI REST API version:
```yaml
model_list:
  - model_name: gpt-5.4-nano
    litellm_params:
      model: azure/gpt-5.4-nano
      api_base: https://oai-ht-taxb-p-eus-01.openai.azure.com/
      api_key: "os.environ/AZURE_API_KEY"
      api_version: "2024-06-01"  # Valid Azure OpenAI REST API version
```

---

### 6. Reasoning Model Parameters (`max_tokens` vs `max_completion_tokens`)

#### Symptom:
* LiteLLM / Azure OpenAI returns:
  `400 Bad Request: Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.`

#### Root Cause:
* The newest generation of Azure OpenAI models (`gpt-5.4-nano`, o1/o3 reasoning models) enforce strict parameter schemas.
* Legacy parameters such as `max_tokens` and custom `temperature` values (other than default 1.0) are disallowed and return `400 Bad Request`.

#### Resolution:
Updated `app/api/routes.py` to use `max_completion_tokens`:
```python
# Before:
resp = await client.post(
    f"{settings.LITELLM_URL}/chat/completions",
    json={
        "model": settings.OPENAI_MODEL,
        "messages": [...],
        "temperature": 0.1,
        "max_tokens": 800,
    }
)

# After:
resp = await client.post(
    f"{settings.LITELLM_URL}/chat/completions",
    json={
        "model": settings.OPENAI_MODEL,
        "messages": [...],
        "max_completion_tokens": 800,
        "user": f"{request.department}:{request.session_id}"
    }
)
```

---

### 7. Kubernetes Image Caching (`imagePullPolicy` & Commit SHA Tagging)

#### Symptom:
* After pushing code fixes and restarting Kubernetes deployments, pods continued to execute old Python code.

#### Root Cause:
* Kubernetes manifests used `image: ...:latest` with `imagePullPolicy: IfNotPresent`.
* When a node already had a local image tagged `:latest`, `kubectl rollout restart` did not re-pull the newly pushed layers from GHCR.

#### Resolution:
1. Changed `imagePullPolicy` to `Always` in `backend-deployment.yaml`.
2. Updated CI/CD pipeline to explicitly tag and set images by **Commit SHA**:
   ```yaml
   IMAGE_LOWER=$(echo "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}" | tr '[:upper:]' '[:lower:]')
   kubectl set image deployment/bankc-backend backend="${IMAGE_LOWER}:${{ github.sha }}" -n bank-compliance
   kubectl rollout status deployment/bankc-backend -n bank-compliance
   ```

---

### 8. Semantic PR Title Validation Failure (`action-semantic-pull-request`)

#### Symptom:
* GitHub Actions job `Validate PR Title (Conventional Commits)` fails with error:
  `No release type found in pull request title "Feature/phase11". Add a prefix to indicate what kind of release this pull request corresponds to.`

#### Root Cause:
* The repository enforces **Conventional Commits** (`amannn/action-semantic-pull-request@v5`) for automated SemVer changelog generation.
* Default branch-based titles (e.g. `Feature/phase11`) lack the required semantic type prefix.

#### Resolution:
* Rename the PR title on GitHub using a valid semantic prefix:
  * `feat: implement GenAIOps CI/CD quality gate, semantic caching, and Helm chart`
  * `fix: resolve LiteLLM 400 parameter issue`
  * `docs: update troubleshooting playbook`

---

### 9. Modern Azure OpenAI Parameter Compatibility

#### Symptom:
* LiteLLM proxy threw `400 BadRequestError`: `Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.`
* Backend fell back to static fallback response for all queries.

#### Root Cause:
* Newer OpenAI and Azure OpenAI flagship deployments (`gpt-5.4-nano`, `gpt-4o`, `o1`, `o3-mini`) strictly deprecate `max_tokens` and enforce `max_completion_tokens`.

#### Resolution:
* Updated `orchestrator.py` and LiteLLM payloads to use `max_completion_tokens: 1024` or omit token caps when targeting modern reasoning models.

---

### 10. Heterogeneous Multi-Agent AI Routing (Google Gemini + Azure OpenAI)

#### Architectural Pattern:
* To balance sub-second latency with deep legal reasoning and zero idle cost:
  1. **Supervisor / Planner Agent:** Invokes `gemini-2.0-flash-lite` via LiteLLM for sub-50ms intent classification and query decomposition.
  2. **Retriever Agent:** Autonomous Qdrant hybrid vector search across indexed RBI Master Directions.
  3. **Auditor / Reflection Agent:** Invokes `gemini-2.0-flash-thinking` via LiteLLM for legal chain-of-thought verification and anti-hallucination guardrails.
  4. **Synthesizer Agent:** Invokes `gemini-2.0-flash` with automatic cross-cloud fallback to Azure OpenAI `gpt-5.4-nano`.

---

### 11. Out-of-Scope Reflection Loop Prevention (Governance Abstention Shield)

#### Symptom:
* When a user asked an unrelated prompt (e.g. *"how to cook chicken"*), the app returned an interpretation of RBI Cloud Data Localization (`RBI/2023-24/108`).

#### Root Cause:
* Qdrant returned 0 matches for cooking, triggering the Auditor reflection retry loop, which fell back to the default banking domain (`it_governance`).

#### Resolution:
* Added fast **Out-of-Scope Intent Classification** in `supervisor_agent.py` and guarded `auditor_agent.py` and `orchestrator.py` with `OUT_OF_SCOPE_RESPONSE_TEMPLATE`, returning an immediate statutory abstention notice without querying banking vectors.

---

### 12. GenAIOps Grafana Command Center & Zero-Baseline Metric Handling

#### Architectural Pillars:
* **Row 1:** 5-Second Executive Health Status Bar (Availability 100%, P95 Latency 96.8ms, 0% 5xx, Quality 93.6%, Safety 100%, Daily Spend).
* **Row 2:** Multi-Model Traffic & Gateway 429 Throttling Rate with `$model` and `$department` variable filters.
* **Row 3:** OpenTelemetry Latency Waterfall Spans (Qdrant Retrieval, Cache Lookup, TTFT, Generation).
* **Row 4:** RAGOps Quality & Groundedness with Soft **Green ($\ge 4.0$) / Yellow / Red** reference bands.
* **Row 5:** BFSI Safety & DPDP Governance (PII Redaction Counters & 100% Adversarial Jailbreak Defense).
* **Row 6:** AI FinOps (Token Velocity, Spend by Model, and Semantic Cache Dollar Savings).
* **Zero-Baseline Fix:** Added `or vector(0)` across all Prometheus queries so empty event windows render clean 0 baselines instead of `"No data"` boxes.

---

### 13. APIM Route Registration for Multi-Agent v2 (LangGraph)

#### Symptom:
* Direct in-cluster calls to `/api/v2/compliance/query` succeeded, but external requests through Azure API Management (`https://apim-ht-ss-p-cin-01.azure-api.net/bankc/api/v2/compliance/query`) failed with `HTTP 404 Resource not found`.

#### Root Cause:
* Azure API Management enforces strict declarative operation whitelisting. Only `/api/v1/compliance/query`, `/healthz`, and `/api/v1/compliance/circulars` were declared under `operations` in `workloads/bank-compliance-ai-aks/apim.tf`.

#### Resolution:
* Added the `compliance-query-v2-post` operation into `workloads/bank-compliance-ai-aks/apim.tf`:
  ```hcl
  "compliance-query-v2-post" = {
    display_name = "Query Compliance v2 (LangGraph)"
    method       = "POST"
    url_template = "/api/v2/compliance/query"
    description  = "Submit regulatory compliance question using LangGraph cyclic StateGraph"
  }
  ```
* Applied cleanly via Terraform: `terraform apply -target="module.bankc_apim_api" -var-file="prod.tfvars" -auto-approve`.

---

### 14. LiteLLM Kubernetes Health Probe Storm & Timeout (`/health` vs `/health/liveness`)

#### Symptom:
* `litellm-proxy` pod went into `0/1 Running` with readiness probe failing: `context deadline exceeded (Client.Timeout exceeded while awaiting headers)`.

#### Root Cause:
* The Kubernetes deployment liveness and readiness probes queried `/health`.
* In LiteLLM Proxy, `/health` triggers synchronous test completions against **every registered backend model** in `model_list` (Gemini, Groq, Azure OpenAI, Ollama). Hitting all upstream models exceeded the 5-second probe timeout.

#### Resolution:
* Replaced heavy `/health` with lightweight native endpoints in `chart/templates/litellm-deployment.yaml`:
  * `livenessProbe.httpGet.path: /health/liveness` (returns `"I'm alive!"` in <10ms).
  * `readinessProbe.httpGet.path: /health/readiness` (returns instant status JSON in <15ms).

---

### 15. Sovereign SLM (`qwen2.5:0.5b`) Helm Chart Model List Alignment

#### Symptom:
* Invoking `model: "private-slm"` via LiteLLM failed with `HTTP 400 Bad Request: Invalid model name passed in model=private-slm`.

#### Root Cause:
* `private-slm` was configured in `app/bank-compliance/k8s/litellm/config.yaml`, but the production Helm chart template `app/bank-compliance/chart/templates/litellm-configmap.yaml` was missing the `private-slm` model entry.

#### Resolution:
* Synchronized `app/bank-compliance/chart/templates/litellm-configmap.yaml` with the complete sovereign SLM definition and updated fallbacks:
  ```yaml
  - model_name: private-slm
    litellm_params:
      model: openai/qwen2.5:0.5b
      api_base: "http://private-slm-inference.bank-compliance.svc.cluster.local:11434/v1"
      api_key: "na"
  ```
* Added `private-slm` to all router fallback cascades across Gemini, Groq, and Azure OpenAI.

---

### 16. Windows PowerShell Line Continuation vs Bash Backslash (`Missing expression after unary operator '--'`)

#### Symptom:
* Pasting multi-line Azure CLI or kubectl commands from documentation into Windows PowerShell errors with:
  ```text
  Missing expression after unary operator '--'.
  Unexpected token 'resource-group' in expression or statement.
  ```

#### Root Cause:
* In Linux/Bash, `\` is the standard line-continuation delimiter. In Windows PowerShell, `\` is treated as a literal argument. PowerShell executes the first line (`az aks get-credentials \`) immediately without its required arguments, and then treats subsequent lines starting with `--flag` as syntax errors (unary negation operators).

#### Resolution:
* In PowerShell, use the **backtick** (`` ` ``) for line continuations, or paste the command as a **single unbroken line**:
  ```powershell
  az aks get-credentials --resource-group rg-ht-bankc-p-cin-01 --name aks-ht-bankc-p-cin-01 --overwrite-existing
  ```
* Multi-line syntax in Windows PowerShell:
  ```powershell
  az aks get-credentials `
    --resource-group rg-ht-bankc-p-cin-01 `
    --name aks-ht-bankc-p-cin-01 `
    --overwrite-existing
  ```
* All runbooks in `docs/confluence/` and `docs/platform-guide/` are dual-formatted with single-line, PowerShell backtick, and Bash snippets.

---

### 17. Client-Side Undeclared JSX Component Runtime Exception (`Uncaught ReferenceError: <Component> is not defined`) & Blank Screen Prevention

#### Symptom:
* Navigating to `https://bank.mytaxbot.site` loads the page title and HTML structure, but the body displays a completely blank/dark screen (`--bg-dark: #07090e`) with no UI elements visible.

#### Root Cause:
* In plain JSX projects (without strict TypeScript compilation enforcing identifier declarations at build time), Vite/Rollup tree-shaking will bundle undeclared identifiers used inside JSX tags (e.g. `<BookOpen />` without `import { BookOpen } from 'lucide-react'`) as references to the global window scope.
* At browser runtime, React executes `React.createElement(BookOpen, ...)`: since `window.BookOpen` is `undefined`, the browser throws `Uncaught ReferenceError: BookOpen is not defined`.
* In React 18, an unhandled render error in any child component causes the entire React root tree to unmount, leaving `<div id="root"></div>` completely empty.

#### Resolution:
1. **Fix Missing Component Imports:**
   * Always import all JSX components and Lucide icons explicitly at the top of the file:
     ```javascript
     import { Send, Bot, Sparkles, BookOpen } from 'lucide-react'
     ```
2. **Implement React Error Boundary (`ErrorBoundary.jsx`):**
   * Wrap the root `<App />` inside a class-based `ErrorBoundary` component in `main.jsx`.
   * If any client-side exception is thrown during rendering, the Error Boundary intercepts the error and presents a sleek enterprise diagnostic card with **"Reload Application"** and **"Reset Local Cache"** buttons along with a collapsible error stack rather than crashing to a pitch-black screen:
     ```jsx
     ReactDOM.createRoot(document.getElementById('root')).render(
       <React.StrictMode>
         <ErrorBoundary>
           <App />
         </ErrorBoundary>
       </React.StrictMode>
     )
     ```
3. **Automate Import Scanning in CI/CD:**
   * Run an automated JSX import validator script across `src/**/*.jsx` prior to deployment to verify that all PascalCase JSX tags match either an explicit ES module import, a standard HTML tag, or a local declaration.

---

### 18. Silent Fallback Bug in Client-Side Document Auditing & Enterprise SPA Dual-Pane URL Routing

#### Symptom:
* In Policy Redliner (`RedlineStudio.jsx`), clearing the editor or typing new draft text continued evaluating to a failing 10% RED score (5 violations). Furthermore, refreshing the page or using browser Back/Forward buttons reset the workspace back to the initial tab because state was monolithic without deep-linkable URL routing.

#### Root Cause:
1. **Silent Fallback Bug:** `runRedlineAudit` had `const currentText = contractText || sampleAgreement`. When `contractText` was empty or cleared, JavaScript truthiness silently audited `sampleAgreement` which contained 5 intentional statutory breaches, triggering a false-positive failure.
2. **Monolithic State:** Navigation pillars lacked HTML5 History (`pushState` / `popstate`) synchronization. Visiting `https://bank.mytaxbot.site/redline` returned to `/copilot`.
3. **Vertical Layout Fatigue:** The legacy layout was vertically stacked (>2,000px high), forcing continuous scrolling between the draft editor and redline diff cards.

#### Resolution:
1. **Default 100% Green State & Dual Sample Loaders:**
   * Provided dual sample loaders:
     * `🟢 Load 100% Compliant Agreement`: Evaluates to 100% Green (0 violations) across all 6 statutory regex rules.
     * `🔴 Load High-Risk SOW (5 Violations)`: Loads the high-risk vendor contract for vulnerability testing.
     * `🧹 Clear Editor`: Resets to a clean state with zero silent fallback.
2. **Deep-Linkable HTML5 URL Routing:**
   * Synchronized navigation with HTML5 History API across `/copilot`, `/command`, `/governance`, `/monitoring`, `/redline`.
   * Handled browser Back/Forward buttons via `popstate` event listeners.
   * Leveraged Azure Static Web Apps `navigationFallback.rewrite = "/index.html"` for direct deep-linking.
3. **Side-by-Side Dual-Pane Workspace:**
   * Left Pane (48% width): Contract Source Editor with word, line, and clause counters.
   * Right Pane (52% width): Sticky Score HUD & scrollable Redline Diff Cards with One-Click Copy and Audit Certificate export.

---

### 19. Eliminating Documentation Sidebar & Split-Screen View Clutter in Enterprise Conversational Copilots

#### Symptom:
* The Regulatory Copilot interface felt visually congested. The conversational chat was constrained into a narrow central column flanked by a 275px left sidebar (listing Master Directions and sector filters), a secondary sub-toolbar with layout switches, and a right-hand document reader pane. Furthermore, secondary sub-headers inside the chat duplicated global controls already established in the top navigation bar.

#### Root Cause:
* Architectural coupling of two distinct user journeys within the same view: (1) Conversational ad-hoc regulatory inquiries, and (2) Statutory documentation browsing/auditing. In enterprise landing zone applications, comprehensive documentation catalogs belong in dedicated Governance / Compliance Centers, whereas conversational copilots deliver peak usability when provided as an expansive, distraction-free canvas.

#### Resolution:
1. **Full-Width Conversational Canvas:**
   * Removed the 275px Master Directions directory sidebar and split `<DocumentViewer>` from the Copilot tab (`App.jsx`).
   * Scaled `<ChatWindow>` to full viewport width with centered reading boundaries (`maxWidth: 880px`).
2. **Eliminated Redundant Headers:**
   * Removed duplicate `REGULATORY SCOPE` and `Inference Mode` subheaders from `ChatWindow.jsx`, relying on the top master executive navigation bar.
3. **Preserved Complete Regulatory Coverage:**
   * Full statutory coverage, clause counts, and SHA-256 provenance hashes remain housed in Pillar 3 (`/governance`), while administrative data lake sync operations remain in Pillar 2 (`/command`).

---

## 3. Platform Engineer Checklist & Golden Rules

| Category | Rule | Verification Command |
| :--- | :--- | :--- |
| **PR Titles** | Follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`. | Check PR title on GitHub UI. |
| **File Encoding** | Always save JSON/YAML/HCL as UTF-8 **without BOM**. | `$b = [System.IO.File]::ReadAllBytes('file'); $b[0..2]` |
| **GHA CI/CD** | Use `$GITHUB_OUTPUT` + `steps.<id>.outputs` for inter-step data. | Check workflow logs for context warnings. |
| **K8s Deployments** | Always use `imagePullPolicy: Always` and commit SHA tags. | `kubectl get deployment bankc-backend -o yaml \| grep image:` |
| **Public APIs** | Always front AKS HTTP services with Azure APIM for SSL/CORS. | `curl -i https://apim-ht-ss-p-cin-01.azure-api.net/bankc/healthz` |
| **Azure OpenAI** | Always verify REST `api-version` format (`YYYY-MM-DD`). | Test raw curl with `?api-version=2024-06-01` |
| **Reasoning Models** | Use `max_completion_tokens` instead of `max_tokens`. | Check LiteLLM pod logs for 400 parameter errors. |
| **GenAIOps Panels** | Wrap Prometheus metric queries with `or vector(0)`. | Verify no "No data" boxes appear on Grafana. |
| **LiteLLM Probes** | Use `/health/liveness` and `/health/readiness`, never `/health`. | `kubectl describe pod litellm-proxy -n bank-compliance` |
| **APIM Operations** | Explicitly register all `/api/v2` endpoints in `apim.tf`. | `az apim api operation list --api-id bankc-compliance-api` |

---

*Authored by HappyTechies AI Platform Engineering Team.*
