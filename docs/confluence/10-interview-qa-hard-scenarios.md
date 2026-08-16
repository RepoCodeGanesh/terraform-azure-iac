# 🎓 10-Yr Azure AI Platform Engineer Interview Guide (Part 2: 30 Very Hard Scenario-Based Dilemmas)

* **Document Code:** `INT-HT-AI-PLATFORM-PART2`
* **Space:** `HappyTechies Cloud & AI Platform` $\rightarrow$ `Interview Masterclass`
* **Target Role:** Principal / Lead Cloud AI Platform Engineer (10+ Years Experience)
* **Topics Covered:** Complex Architecture Dilemmas, Split-Brain State, OOM Recovery, WIF Token Hardening, Multi-Region Failover, Zero Data Retention & FinOps Fail-Safes

---

## 🏛️ Theme 1: Terraform IaC, Cross-Subscription & State Scenarios (Q1 – Q6)

### Scenario 1: Multi-Root State Deadlock & Split-Brain Drift
**Scenario:** A senior engineer modifies `modules/vnet_peering` and triggers the GitHub Actions pipeline for `workloads/tax-advisor` and `workloads/bank-compliance-ai-aks` simultaneously. Both pipelines attempt to create peering to the Hub VNet at the exact same second. The Hub-prod peering resource fails with a `409 Conflict: VirtualNetworkPeeringOperationInProgress`, leaving the spoke state half-applied. How do you design the architecture and pipeline concurrency to guarantee deterministic execution?
**Solution:**
1. **GitHub Actions Concurrency Groups:** Implement `concurrency: group: hub-peering-${{ matrix.workload }}` with `cancel-in-progress: false` to enforce sequential FIFO execution on shared network resources.
2. **Terraform Lock Timeout:** Set `-lock-timeout=10m` in `terraform apply` to allow transient ARM locks to clear.
3. **Idempotent Peering Retries:** Wrap the peering module with exponential backoff or manage Hub-side peering centrally in `platform/hub` reading spoke VNet IDs via remote state data sources (`terraform_remote_state`), eliminating concurrent write collisions on the Hub VNet.

---

### Scenario 2: ARM RBAC Propagation Lag (The 403 Authorization Race Condition)
**Scenario:** In a single Terraform run in `workloads/bank-compliance-ai-aks`, you create a User-Assigned Managed Identity (`uami-ht-bankc-p-cin-01`), assign it `Cognitive Services User` role on Content Safety (`cs-ht-bankc-p-sea-01`), and deploy the AKS Federated Identity Credential. The apply intermittently fails with `403 Forbidden: Caller does not have permissions to perform action on resource`. Why does this happen in Azure Entra ID, and how do you architect a zero-failure Terraform pattern?
**Solution:**
1. **Root Cause:** Azure Entra ID and Azure Resource Manager RBAC have a globally distributed eventual consistency replication window (typically 30–90 seconds).
2. **Architectural Fix:**
   * Pre-provision identity lifecycle in a dedicated identity layer or use explicit DAG sequencing.
   * Introduce a `time_sleep` resource (from `hashicorp/time` provider) with `create_duration = "60s"` between the `azurerm_role_assignment` and the dependent resource.
   * Set explicit `depends_on = [time_sleep.wait_for_rbac_propagation]`.

---

### Scenario 3: Terraform State File Recovery after Blind Backend Deletion
**Scenario:** An auditor accidentally revokes the pipeline's permissions to the bootstrap storage account container `tfstate`, and a junior engineer runs `terraform init -reconfigure`, accidentally initializing a fresh local state and running `terraform apply`, creating duplicate resource naming conflicts (`ResourceExistsError`). How do you recover the original remote state and reconcile Terraform without destroying live production infrastructure?
**Solution:**
1. **Restore Storage Access:** Re-assign `Storage Blob Data Owner` role on `sthtbootpcin01` to the platform admin identity.
2. **Blob Versioning Recovery:** Azure Storage Blob Versioning is enabled on `sthtbootpcin01`. Navigate to `tfstate/workloads/tax-advisor/prod.tfstate` and restore the latest valid historical snapshot.
3. **State Re-alignment:** Run `terraform init -backend-config=backend.hcl -reconfigure`.
4. **Targeted State Refresh:** Execute `terraform refresh -var-file=prod.tfvars` to synchronize the state with actual Azure ARM state.
5. **State Import Reconciliation:** For any orphaned resources created during the rogue run, use `terraform import` or delete rogue orphan resources from Azure Portal prior to the next CI/CD run.

---

### Scenario 4: Subnet Delegation Deadlock during Terraform Destroy / Update
**Scenario:** You attempt to update the subnet address space of `snet-aks-p-cin-01` in `workloads/bank-compliance-ai-aks`. Terraform fails stating that the subnet cannot be modified or deleted because it has active delegations or linked IP configurations from a lingering Network Interface (NIC). How do you resolve this without causing cluster downtime?
**Solution:**
1. **Root Cause:** AKS nodes create VMSS Network Interfaces that maintain active leases on the subnet CIDR. Subnet prefixes cannot be changed while active NICs exist.
2. **Zero-Downtime Resolution Pattern (Dual Subnet Migration):**
   * Step 1: Provision a new secondary subnet (`snet-aks-p-cin-02`) via Terraform.
   * Step 2: Add a new node pool in AKS attached to `snet-aks-p-cin-02`.
   * Step 3: Cordon and drain nodes on the old node pool (`kubectl drain <node> --ignore-daemonsets --delete-emptydir-data`).
   * Step 4: Delete the old node pool once workloads migrate.
   * Step 5: Safely remove `snet-aks-p-cin-01` in Terraform.

---

### Scenario 5: Cross-Tenant OIDC Token Replay Vulnerability & Subject Claim Hardening
**Scenario:** A security pen-tester discovers that your GitHub Actions workflow uses OpenID Connect (WIF) to authenticate with Entra ID. They fork your repository to a public GitHub organization and attempt to run a malicious workflow against your Azure subscription. How does your Entra ID Federated Credential configuration prevent this attack?
**Solution:**
* **Subject Identifier Hardening:** Entra ID validates the exact sub-claim structure in the JWT issued by `token.actions.githubusercontent.com`:
  $$\text{Subject: } \mathbf{repo:\langle Org\rangle/\langle Repo\rangle:environment:\langle EnvironmentName\rangle}$$
* A fork will produce `repo:HackerOrg/terraform-azure-iac:...`, which Entra ID immediately rejects with `AADSTS7000215: Invalid client assertion`.
* **Audience Validation:** Lock audience strictly to `api://AzureADTokenExchange`.
* **Branch/Environment Protection Rules:** Enforce GitHub repository environment protection rules requiring manual approval from designated leads before secrets are exposed to workflows.

---

### Scenario 6: Terraform Dynamic Provider Configuration Failure in CI/CD
**Scenario:** A developer tries to use `azurerm_kubernetes_cluster.bank_compliance.kube_config.0.client_certificate` inside a `kubernetes` or `helm` provider block in the same Terraform root. The first run succeeds, but during cluster upgrade/refresh, Terraform crashes with `Provider produced inconsistent final plan` or `Error: Post "https://aks-...": dial tcp: lookup failed`. Why is this an anti-pattern, and what is the enterprise standard?
**Solution:**
* **Root Cause (The Interpolated Provider Anti-Pattern):** HashiCorp strongly advises against interpolating resource attributes into provider blocks. During refresh/plan, Terraform needs provider configuration *before* evaluating resources. If AKS is being destroyed or updated, the provider configuration becomes unknown or unresolvable.
* **Enterprise Standard (Decoupled Toolchain):**
  * **Layer 1 (Terraform):** Deploys the AKS cluster, networking, and Managed Identities, outputting cluster credentials.
  * **Layer 2 (Helm / GitOps via Flux/ArgoCD or GitHub Actions):** Consumes credentials in a downstream pipeline job via `az aks get-credentials` and deploys Helm charts independently.

---

## ☸️ Theme 2: AKS, Kubernetes Networking & Storage Scenarios (Q7 – Q12)

### Scenario 7: Azure CNI Overlay Routing & Spoke-to-Hub Asymmetric Routing
**Scenario:** A pod inside AKS (`192.168.1.15`) attempts to connect to an internal APIM Gateway (`10.0.1.10`) in Shared Services through the Hub Firewall. Traffic reaches APIM, but the response is dropped, resulting in `504 Gateway Timeout`. Kube-proxy and node routing look healthy. What is the root cause and how do you fix it?
**Solution:**
* **Root Cause (Asymmetric Routing / SNAT):** In Azure CNI Overlay, pods use non-VNet overlay IPs (`192.168.0.0/16`). When pod traffic leaves the node towards the VNet, the node performs Source NAT (SNAT) by default. If a User-Defined Route (UDR) forces traffic through Azure Firewall, but return traffic bypasses the firewall (or vice versa), the firewall drops the stateful connection.
* **Fix:**
  1. Configure `ip-masq-agent` ConfigMap on AKS to non-masquerade traffic destined for internal corporate CIDRs (`10.0.0.0/8`, `172.16.0.0/12`).
  2. Ensure UDRs on the AKS node subnet point `0.0.0.0/0` and corporate prefixes to the Hub Firewall virtual appliance IP.

---

### Scenario 8: Qdrant Vector Index Storage Deadlock across `az aks stop` / `az aks start`
**Scenario:** The FinOps scheduler stops the AKS cluster at 7:30 PM. At 8:00 AM, `az aks start` executes. The node pool boots up, but the Qdrant pod remains in `ContainerCreating` state for 15 minutes, logging `Multi-Attach error for volume: Volume is already exclusively attached to one node and can't be attached to another`. How do you resolve this CSI volume attachment race condition?
**Solution:**
* **Root Cause:** When the cluster deallocates, Azure's compute fabric marks the VM as deallocated before the Azure Disk CSI driver can gracefully unmount the LUN attachment from Azure Resource Manager storage fabric. On startup, a new VM node ID is assigned, but ARM storage still sees the disk attached to the old deallocated VM ID.
* **Architectural Fix:**
  1. Add a graceful pre-stop hook in GitHub Actions: Run `kubectl scale deployment/qdrant --replicas=0 -n bank-compliance` 2 minutes *before* issuing `az aks stop`. This unmounts the CSI disk cleanly.
  2. In `k8s/qdrant/values.yaml`, ensure `podManagementPolicy: OrderedReady` and use a `StatefulSet` with `volumeClaimTemplates` rather than a loose deployment.

---

### Scenario 9: Ephemeral OS Disk Sizing Eviction & `ImagePullBackOff`
**Scenario:** You deploy a developer's test container image (6GB uncompressed) to the `Standard_B4ms` node pool with Ephemeral OS. The pod fails to start with `ImagePullBackOff: failed to extract image: no space left on device`, and existing pods are evicted with `DiskPressure`. Why did this happen, and how do you size ephemeral disks properly?
**Solution:**
* **Root Cause:** `Standard_B4ms` provides a temporary cache disk of **32 GiB**. When `os_disk_size_gb = 30` is allocated for Ephemeral OS, the root filesystem, container runtime cache (`/var/lib/containerd`), image layers, and emptyDir volumes all share those 32 GiBs. Pulling large images exhausts the cache immediately.
* **Fix:**
  1. **Image Optimization:** Multi-stage Docker builds using `python:3.11-slim` or `distroless` to keep container images <250MB.
  2. **Image Garbage Collection Tuning:** Configure Kubelet flags `imageGCHighThresholdPercent: 70` and `imageGCLowThresholdPercent: 50`.
  3. **High-Memory Node Upgrade:** For larger workloads, upgrade node pool to `Standard_D4ds_v5` (which provides 150GB NVMe ephemeral cache).

---

### Scenario 10: OPA Gatekeeper Admission Controller Outage during AKS Upgrade
**Scenario:** During a minor Kubernetes version upgrade (`1.29` $\rightarrow$ `1.30`), the OPA Gatekeeper webhook pod is terminating on an old node while the control plane sends admission review requests. Developers deploying emergency hotfixes find all `kubectl apply` commands blocked with `Error from server (InternalError): Internal error occurred: failed calling webhook "validation.gatekeeper.sh"`. How do you configure Gatekeeper webhooks to prevent deployment deadlocks during cluster maintenance?
**Solution:**
* **Root Cause:** The `ValidatingWebhookConfiguration` for Gatekeeper was configured with `failurePolicy: Fail` (Fail-Closed) with a single webhook replica.
* **Fix:**
  1. Deploy at least **2 replicas** with Pod Disruption Budgets (`minAvailable: 1`) and anti-affinity across nodes.
  2. In the webhook configuration, set `failurePolicy: Ignore` (Fail-Open) for internal system namespaces (`kube-system`, `gatekeeper-system`) and non-critical deployments, while retaining `Fail` only for security-critical production namespaces.
  3. Set a reasonable `timeoutSeconds: 3` to prevent API server thread exhaustion.

---

### Scenario 11: KEDA Scale-to-Zero Cold Start Latency Mitigation for High-Value Queries
**Scenario:** Bank compliance officers report that the first query of the morning takes **12 to 18 seconds** to respond because KEDA scaled the backend pod to 0 replicas overnight. The sub-second SLA (<800ms) is severely breached. How do you eliminate cold-start latency while maintaining near-zero idle compute costs?
**Solution:**
1. **Pre-Warming FinOps Hook:** Update `.github/workflows/finops-scheduler.yml` to dispatch a synthetic "wake-up" query 15 minutes before branch opening hours (e.g. 8:45 AM IST), prompting KEDA to scale replicas to 1.
2. **KEDA Cooldown Period Optimization:** Increase `cooldownPeriod: 1800` (30 minutes) so pods remain warm during intermittent morning traffic.
3. **LiteLLM Edge Absorption:** Configure LiteLLM Gateway pod (which always stays running at 0.05 vCPU) to serve common cached compliance queries in <20ms while the backend pod spins up asynchronously.

---

### Scenario 12: Private AKS Cluster vs API Server Public Authorized IP Ranges
**Scenario:** A banking security auditor demands that the AKS cluster API server be completely private (`enable_private_cluster = true`). However, developers need to run GitHub Actions CI/CD and Azure DevOps pipelines from cloud-hosted runners without paying $300/month for a dedicated Azure Bastion and private runner VM. How do you satisfy the security requirement at zero additional cost?
**Solution:**
* **Enterprise Pattern:** Use **API Server Authorized IP Ranges** (`api_server_authorized_ip_ranges`) combined with **GitHub Actions OIDC IP dynamic whitelisting** or use **AKS Run Command API** (`az aks command invoke`):
  * `az aks command invoke` runs `kubectl` commands through the Azure ARM management plane (authenticated via Entra ID WIF OIDC) directly into the AKS control plane without requiring the GitHub runner to have network line-of-sight to the private API server.
  * This delivers 100% private cluster security with **$0 runner VM hosting cost**.

---

## 🤖 Theme 3: AI Gateway, LiteLLM & Vector RAG Scenarios (Q13 – Q18)

### Scenario 13: Cascading 429 Throttling Storm across Regional Outages
**Scenario:** Azure OpenAI in `East US` experiences a regional capacity degradation, returning `429 Too Many Requests` on `gpt-5.4-nano`. The FastAPI backend begins retrying aggressively, exhausting local node connections and causing APIM Gateway to throw `500 Internal Server Errors` across all users. How do you design LiteLLM resiliency to handle upstream AI outages gracefully?
**Solution:**
1. **Multi-Region Fallback Router:** Configure LiteLLM `router_settings` with active-passive regional endpoints:
   ```yaml
   model_list:
     - model_name: gpt-5.4-nano
       litellm_params:
         model: azure/eastus/gpt-5.4-nano
         api_base: https://oai-ht-taxb-p-eus-01.openai.azure.com/
     - model_name: gpt-5.4-nano
       litellm_params:
         model: azure/centralindia/gpt-5.4-nano
         api_base: https://oai-ht-bankc-p-cin-01.openai.azure.com/
   router_settings:
     routing_strategy: "latency-based-routing"
     allowed_fails: 3
     cooldown_time: 60
   ```
2. **Exponential Backoff with Jitter:** Configure client-side retry policies using exponential backoff with full jitter to avoid the thundering herd problem.
3. **Circuit Breaking in APIM:** Enable circuit breaker policies in Azure APIM Gateway to return a graceful degraded response (serving pre-indexed regulatory text) when downstream error rates exceed 30%.

---

### Scenario 14: Qdrant HNSW Memory Spike & OOMKilled Disaster Recovery
**Scenario:** During an automated ingestion batch of 5,000 new compliance circular clauses, Qdrant memory usage spikes from 250MB to 1.8GB during vector graph construction (`ef_construct: 512`), exceeding the pod memory limit (`limits.memory: 1Gi`). Kubernetes sends `SIGKILL` (`OOMKilled`, Exit Code 137). Qdrant restarts, re-indexes, and OOM-crashes in a crash loop. How do you resolve this?
**Solution:**
1. **Immediate Crash Loop Resolution:**
   * Temporarily increase memory limit in Helm values to 2Gi, or configure Qdrant `memmap_threshold_kb: 50000` to force memory-mapping vectors directly to the 4GB CSI disk rather than keeping raw vectors in RAM.
2. **HNSW Parameter Optimization:**
   * Lower `ef_construct: 128` and `m: 16` during ingestion. This reduces memory usage during index construction by 65% with <1% degradation in recall.
3. **Chunked Ingestion Pipeline:**
   * Modify `rbi_chunker.py` to batch upserts in chunks of 100 vectors with a 500ms pause between batches, allowing garbage collection to reclaim memory.

---

### Scenario 15: Prompt Cache Poisoning & Stale Regulatory Interpretation Risks
**Scenario:** The Reserve Bank of India (RBI) issues an emergency amendment overriding Section 4.2(a) of the KYC Master Direction. However, LiteLLM's in-memory prompt cache is serving cached interpretations from the previous week in <20ms, causing the AI to provide legally invalid compliance guidance. How do you design cache eviction governance for regulatory RAG?
**Solution:**
1. **Dynamic Cache Tagging:** Configure LiteLLM cache keys to include a regulatory corpus version hash:
   $$\text{Cache Key: } \mathbf{Hash(Query + \text{rbi\_corpus\_version\_v2026.08.15})}$$
2. **Event-Driven Cache Purge:** When a new circular is ingested into Qdrant, the ingestion script dispatches an administrative cache invalidation call to LiteLLM: `POST /cache/flush?tag=kyc_master_direction`.
3. **Time-To-Live (TTL) Policy:** Reduce maximum cache TTL from 7 days to `7200s` (2 hours) for regulatory domains.

---

### Scenario 16: Zero Data Retention (ZDR) Legal Audit Verification
**Scenario:** A bank internal audit team demands cryptographic proof that no confidential banking prompts, employee queries, or compliance inquiries are stored, logged, or retained on Microsoft servers for LLM retraining. How do you architect and prove Zero Data Retention compliance?
**Solution:**
1. **Microsoft Enterprise ZDR Agreement:** Submit and approve the Azure OpenAI **Modified Abuse Monitoring & Data Logging Exemption**. This disables Microsoft's automated asynchronous content filtering logs and human review pipeline.
2. **Stateless Gateway Verification:** Verify in `function_app.py` and LiteLLM configurations that `store_prompts = false`.
3. **Application Insights Log Scrubbing:** Ensure telemetry initializers in OpenTelemetry explicitly strip `prompt_text` and `completion_text` from custom dimensions before streaming traces to Log Analytics.

---

### Scenario 17: Multi-Tenant Token Quota Starvation across Bank Departments
**Scenario:** The Wealth Management department runs an automated statutory analysis script that consumes 200,000 tokens in 10 minutes. The Retail Banking and Fraud Monitoring teams find all their compliance copilot queries rejected with `429 Token Budget Exceeded`. How do you implement multi-tenant quota isolation in LiteLLM?
**Solution:**
1. **LiteLLM Virtual Keys:** Issue distinct API keys per department (`dept-wealth-key`, `dept-retail-key`, `dept-fraud-key`).
2. **Hierarchical Token Budgeting:**
   ```yaml
   keys:
     - key: dept-wealth-key
       max_budget: 15.00 # $15/day budget
       tpm_limit: 20000
       rpm_limit: 30
     - key: dept-retail-key
       max_budget: 30.00
       tpm_limit: 40000
   ```
3. **Rate Limiting at APIM:** Configure APIM rate-limiting policies segmented by HTTP header `X-Department-ID`.

---

### Scenario 18: Vector Semantic Drift & Hallucination Suppression
**Scenario:** A compliance officer asks: *"What is the penalty for failure to localize credit card transaction data?"* The vector database retrieves a clause on *loan data localization* with high cosine similarity (0.88). The LLM generates a convincing but factually incorrect penalty citation. How do you suppress semantic drift hallucinations in legal RAG?
**Solution:**
1. **Metadata Pre-Filtering:** In `qdrant_service.py`, apply hard metadata filter constraints before vector search:
   `Filter(must=[FieldCondition(key="domain", match=MatchValue(value="credit_cards"))])`.
2. **Cross-Encoder Re-ranking:** Pass top 10 retrieved chunks through a lightweight cross-encoder model to re-score query-document relevance, discarding chunks scoring below a strict confidence threshold (0.75).
3. **Strict System Prompt Grounding:** Constrain the system prompt: *"If the provided context does not explicitly contain the statutory penalty for credit cards, respond: 'Statutory penalty not specified in retrieved clauses - Refer to RBI Master Direction Section X'."*

---

## 🛡️ Theme 4: Security, Identity & Regulatory Governance Scenarios (Q19 – Q24)

### Scenario 19: Multi-Modal / Document Attachment PII Exfiltration
**Scenario:** A user uploads a scanned PDF copy of a customer's loan application containing handwritten PAN, Aadhaar, and bank statements into the chat window. The text regex redactor only processes raw string text and misses the PDF attachment, transmitting raw PII to the cloud LLM. How do you design an enterprise multi-modal PII redaction pipeline?
**Solution:**
1. **Pre-Processing OCR Sandbox:** Route all uploaded PDFs/images through an ephemeral in-memory OCR service (Azure AI Vision Read API or Tesseract) in an isolated spoke container.
2. **Named Entity Recognition (NER) Redaction:** Run extracted text through Azure AI Language Service PII recognition API (configured with `domain = "ProtectedHealthcareAndFinancialInformation"`), replacing all detected Indian PII entities with generic entity tags (`<PII:PAN_NUMBER>`, `<PII:AADHAAR>`).
3. **Image Pixel Masking:** For visual attachments, redact bounding box coordinates corresponding to sensitive PII before any image is forwarded to multi-modal vision models.

---

### Scenario 20: Compromised Pod Lateral Movement Attack Simulation
**Scenario:** An attacker exploits a vulnerability in a third-party Python package inside the FastAPI backend container and obtains a reverse shell inside the pod. What architectural guardrails prevent the attacker from stealing storage keys, accessing other departments' databases, or compromising the AKS node?
**Solution:**
1. **No Cloud Secrets in Pod:** Pod uses Workload Identity; there are no Azure storage connection strings, service principal client secrets, or API keys in environment variables or filesystem.
2. **Non-Root Execution:** OPA Gatekeeper prevents the container from running as `root`, preventing kernel exploitation.
3. **Kubernetes NetworkPolicy Isolation:** Default-deny egress policy blocks the pod from scanning internal VNet subnets (`10.0.0.0/16`) or communicating with pods in other namespaces.
4. **IMDS Metadata Protection:** Azure IMDS endpoint (`169.254.169.254`) is blocked or restricted via Azure CNI NetworkPolicies, preventing the attacker from requesting node-level managed identity tokens.

---

### Scenario 21: Log Analytics 5GB Daily Cap Exhaustion & Telemetry Dropping
**Scenario:** A misconfigured debug log level in the backend generates 15 GB of logs in 3 hours. The central Log Analytics Workspace (`law-ht-ss-p-cin-01`) hits its 5GB Free Tier daily cap and stops ingesting all platform telemetry, blinding security monitoring for the rest of the day. How do you protect logging infrastructure from runaway cost and ingestion denial?
**Solution:**
1. **Daily Cap Alerts:** Configure Azure Monitor alert on Log Analytics Workspace metric `OverQuotaVolume` firing at 80% (4GB).
2. **Log Ingestion Filtering:** Configure Data Collection Rules (DCR) in Azure Monitor to drop `DEBUG` and verbose `HTTP 200 OK` healthcheck logs before ingestion.
3. **Namespace Isolation:** Deploy separate Log Analytics workspaces for non-production environments to isolate production audit logging from dev/sandbox data spikes.

---

### Scenario 22: Content Safety False-Positive Blocking on Legitimate Audit Inquiries
**Scenario:** A Chief Compliance Officer submits a legitimate query: *"What are the RBI guidelines for reporting employee bribery, extortion, and cyber fraud?"* Azure AI Content Safety flags the query under the `Violence/Harm` category and blocks the request with a `400 Content Safety Violation`. How do you tune Content Safety for legal compliance workflows without creating security loopholes?
**Solution:**
1. **Category Severity Calibration:** In `modules/content_safety`, adjust category severity threshold levels from `Low (2)` to `Medium (4)` for compliance-specific deployments.
2. **Custom Blocklists & Allow-lists:** Create an Azure AI Content Safety Blocklist / Allowlist containing statutory legal terms (e.g. *bribery, extortion, money laundering, fraud reporting*) to prevent false-positive trigger classifications.
3. **Human-in-the-Loop Review Pipeline:** When a query is flagged, route it to an internal Compliance Officer Review queue in Cosmos DB rather than returning a generic error to the user.

---

### Scenario 23: Cross-Subscription VNet Peering Route Poisoning
**Scenario:** A rogue administrator in `Apps-prod` configures a User-Defined Route (UDR) table on `snet-aks-p-cin-01` routing `10.0.0.0/8` to an unvetted virtual appliance IP, hijacking corporate traffic destined for the Shared Services APIM Gateway. How does your Landing Zone governance prevent spoke route poisoning?
**Solution:**
1. **Azure Policy Route Table Governance:** Deploy an Azure Policy definition enforcing that all UDRs attached to spoke subnets must have `nextHopIpAddress` matching the official Hub Firewall IP (`10.0.0.4`).
2. **RBAC Scope Demarcation:** Spoke workload engineers are assigned `Contributor` only at the resource group level (`rg-ht-bankc-p-cin-01`), while route tables and subnet modifications require `Network Contributor` at the Subscription scope, strictly controlled by the Platform Team.
3. **Hub BGP Route Propagation:** Disable route propagation on untrusted spoke route tables.

---

### Scenario 24: Key Vault HSM vs Standard Sizing for Financial Compliance
**Scenario:** An enterprise security audit mandates compliance with **FIPS 140-2 Level 3** for customer data encryption keys. The current Landing Zone uses Azure Key Vault Standard (`Standard` SKU, FIPS 140-2 Level 2). What is the migration strategy, cost impact, and Terraform architecture change?
**Solution:**
1. **SKU Transition:** Upgrade Key Vault from `standard` to `premium` (or deploy dedicated **Azure Key Vault Managed HSM**).
2. **Cost Impact:** Key Vault Premium costs fractions of a cent per operation; Managed HSM costs ~$4.50/hour (~$3,200/month). For low-cost compliance, Key Vault Premium HSM-protected keys (`RSA-HSM`) provide FIPS 140-2 Level 3 compliance at <$1/month.
3. **Terraform Update:** Update `modules/key_vault/variables.tf` to set `sku_name = "premium"`. Terraform performs an in-place upgrade without destroying existing keys or secrets.

---

## 💰 Theme 5: Advanced FinOps, Scalability & Disaster Recovery (Q25 – Q30)

### Scenario 25: Burstable VM Credit Bank Exhaustion during Unscheduled Audit
**Scenario:** Financial auditors arrive for an unannounced inspection and run 500 concurrent statutory queries against BankCompliance AI. The `Standard_B4ms` node exhausts its CPU credit bank in 25 minutes. CPU throttles to 22.5%, and query response times degrade from 600ms to 24 seconds. How do you architect an emergency burstable fail-safe?
**Solution:**
1. **Automated CPU Credit Alert:** Configure an Azure Monitor alert on metric `CPUCreditsRemaining < 50`.
2. **KEDA Emergency Scale-Out:** Configure KEDA to scale out node pools via AKS Cluster Autoscaler if average CPU exceeds 65% for 3 consecutive evaluation periods.
3. **Option A Advantage:** Because Option A routes queries to Azure OpenAI (`gpt-5.4-nano`) via LiteLLM, node CPU consumption is only ~3%. Even under 500 concurrent queries, CPU load does not exceed 15%, leaving the credit bank 100% full.

---

### Scenario 26: Multi-Region Disaster Recovery (RTO < 5 min, RPO = 0) for AI Copilots
**Scenario:** A catastrophic submarine cable outage takes down the entire Azure `Central India` region. Management demands that both TaxBot India and BankCompliance AI fail over to `South India` or `East US` with a Recovery Time Objective (RTO) of < 5 minutes and zero data loss. What is the Disaster Recovery architecture?
**Solution:**
1. **Stateless Compute Portability:**
   * Static Web Apps are globally distributed via Azure Front Door / global CDN.
   * Container images are replicated across regions via `ghcr.io`.
2. **Storage Replication (RPO = 0):**
   * Cosmos DB configured with multi-region write / active-active geo-replication (`Central India` + `South India`).
   * Qdrant Vector DB snapshot automated nightly to Geo-Redundant Storage (GRS) container `sthtbootpcin01`.
3. **DNS Failover (RTO < 2 min):**
   * Traffic Manager / Azure Front Door health probes detect Central India outage and route custom subdomains (`bank.mytaxbot.site`) to secondary region endpoint in <60 seconds.

---

### Scenario 27: Blue-Green Zero-Downtime AKS Control Plane Upgrade Strategy
**Scenario:** Kubernetes `1.28` reaches End-of-Life (EOL). Upgrading the control plane and node pool in-place risks transient API downtime and CSI storage re-attachment locks. How do you execute a Blue-Green cluster migration using Terraform and GitOps?
**Solution:**
1. **Green Cluster Provisioning:** Terraform provisions `aks-ht-bankc-p-cin-02` (Green) alongside `aks-ht-bankc-p-cin-01` (Blue) in a secondary spoke subnet.
2. **Workload Deployment:** Deploy Qdrant and LiteLLM Helm charts to Green cluster; sync vector database snapshot from GRS backup.
3. **Canary Traffic Shift:** In Azure APIM Gateway, update backend routing policy to shift 10% $\rightarrow$ 50% $\rightarrow$ 100% of traffic to the Green cluster.
4. **Decommission Blue Cluster:** Once health probes pass for 24 hours, destroy `aks-ht-bankc-p-cin-01` in Terraform.

---

### Scenario 28: Zero-Trust APIM Gateway Backend Certificate Pinning & Mutual TLS (mTLS)
**Scenario:** A bank security mandate requires Mutual TLS (mTLS) and certificate pinning between the shared APIM Gateway in `Shared-services` and the private AKS Ingress Controller in `Apps-prod`. How is this architected in Terraform?
**Solution:**
1. **Internal Ingress Controller:** Deploy NGINX Ingress Controller on AKS with internal load balancer IP (`10.42.1.200`).
2. **Client Certificate Issuance:** Generate an enterprise root CA certificate stored in Shared Key Vault (`kv-ht-ss-p-cin-01`).
3. **APIM Backend Configuration:** Configure `azurerm_api_management_backend` with `client_certificate_id` referencing the Key Vault certificate.
4. **NGINX mTLS Enforcement:** Configure NGINX Ingress with annotations `nginx.ingress.kubernetes.io/auth-tls-verify-client: "on"` and `nginx.ingress.kubernetes.io/auth-tls-secret: "bank-ca-secret"`.

---

### Scenario 29: AI Search Index Corruption & Vector Backfill Strategy
**Scenario:** An index schema migration on Azure AI Search (`srch-ht-taxb-p-cin-01`) corrupts the vector index during a tax season peak. TaxBot India is unable to retrieve statutory provisions. How do you restore search operations in under 3 minutes?
**Solution:**
1. **Blue-Green Indexing Pattern:** Always maintain two indexes (`tax-statutes-v1` and `tax-statutes-v2`) in Azure AI Search.
2. **Index Alias Abstraction:** The Function App queries index alias `tax-statutes-active`.
3. **Instant Re-pointing:** If `tax-statutes-v2` is corrupted, issue an instant REST call to update the alias back to `tax-statutes-v1` in **<2 seconds** without modifying application code or redeploying the function.

---

### Scenario 30: 10-Year Architect Vision: Autonomous Self-Healing AI Landing Zone
**Scenario:** As Lead AI Platform Architect, an executive asks you: *"How will this Azure AI platform scale over the next 5 years to support 50+ enterprise copilots across multiple departments while keeping infrastructure headcount flat and idle costs near zero?"* How do you articulate the technical vision?
**Solution:**
1. **Platform Engineering & Developer Portals:** Transition from manual IaC tickets to an internal developer platform (Backstage / Azure Deployment Environments) where business teams self-serve pre-approved, compliance-hardened copilot spoke templates in <10 minutes.
2. **Multi-Tenant Gateway Mesh:** Central APIM and LiteLLM gateways scale out dynamically to route across 50+ departmental copilots with automated chargebacks, global rate limits, and cross-region AI load balancing.
3. **Automated Continuous Compliance:** Azure Policy and OPA Gatekeeper continuously enforce security guardrails at pull-request time, ensuring 100% audit readiness with zero manual compliance overhead.
4. **Serverless & Burstable FinOps Core:** Every copilot adheres to the **Scale-to-Zero** design pattern, keeping cumulative idle cloud expenditures for 50 applications under **$15/month**.
