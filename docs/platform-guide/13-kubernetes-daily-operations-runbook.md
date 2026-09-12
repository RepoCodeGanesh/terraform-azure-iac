# Platform Guide 13 — Enterprise Kubernetes Daily Operations Runbook

[← Back to Master Index](README.md)

---

## 📋 Executive Overview & Purpose

This operational runbook provides cloud engineers, AI platform architects, and SREs with a standardized, production-tested command reference for managing **Azure Kubernetes Service (AKS)** hosting the **BankCompliance AI** workload.

Every command in this guide includes:
1. **Command Syntax & Exact Flags**: Real-world CLI invocations targeting our monorepo namespace architecture (`bank-compliance`, `monitoring`, `ingress-nginx`, `kube-system`).
2. **Operational Purpose**: Clear rationale explaining *why* and *when* the command is used during day-to-day operations.
3. **Expected Output & Diagnostics**: Guidance on interpreting the terminal output and identifying anomalous states.

```text
+---------------------------------------------------------------------------------------------------+
|                            AKS ENTERPRISE CLUSTER TOPOLOGY & NAMESPACES                           |
+---------------------------------------------------------------------------------------------------+
| Cluster: aks-ht-bankc-p-cin-01 | RG: rg-ht-bankc-p-cin-01 | Region: Central India (cin)           |
+------------------------------------+----------------------------------+---------------------------+
| [bank-compliance] Namespace        | [monitoring] Namespace           | [ingress-nginx] Namespace |
| • bankc-backend (FastAPI RAG)      | • monitoring-grafana (Port 3000) | • ingress-nginx-controller|
| • litellm-proxy (Port 4000)        | • prometheus-server (Port 9090)  | • Ingress routing rules   |
| • qdrant (Vector DB, Port 6333)    | • kube-state-metrics             | • TLS/SSL termination     |
| • private-slm-inference (Port 11434)|                                 |                           |
| • bankc-mcp-server (Port 8080)     |                                  |                           |
+------------------------------------+----------------------------------+---------------------------+
```

---

## 🧭 Command Matrix: Quick Navigation

| Tier | Focus Area | Primary Target Resources | When to Use |
|:---|:---|:---|:---|
| **Tier 1** | Cluster Access & Identity | `az aks get-credentials`, Contexts | Shift handover, session startup, role validation |
| **Tier 2** | Cluster Health & Capacity | Nodes, CPU/Memory metrics, Headroom | Morning health check, sizing verification, pre-deploy |
| **Tier 3** | Pod Lifecycle & Deployment | Deployments, ReplicaSets, Rollouts | Application release, zero-downtime restart, rollbacks |
| **Tier 4** | Logs & Deep Diagnostics | Multi-container pods, Init containers | Debugging 500s, SLM model pulling, prompt failures |
| **Tier 5** | Zero-Trust Port-Forwarding | Grafana, Qdrant, LiteLLM, FastMCP | Safe local debugging without public IP exposure |
| **Tier 6** | Helm Release Lifecycle | Helm releases, stuck state secrets | Helm timeouts, pending-upgrade recovery |
| **Tier 7** | FinOps & Scaling Controls | Replicas, KEDA ScaledObjects | Nightly idle shutdown, cost optimization |
| **Tier 8** | Config, Secrets & Storage | ConfigMaps, Secrets, PVCs, CSI | Rotating API keys, verifying storage mounts |
| **Tier 9** | Network & DNS Diagnostics | CoreDNS, Services, Ingress, Egress | Investigating connection timeouts, resolving DNS |

---

## 🔐 Tier 1: Cluster Access, Context & Entra ID Identity

### 1.1 Connect to Production AKS Cluster

**Single-Line (Recommended across Windows PowerShell, macOS & Linux):**
```bash
az aks get-credentials --resource-group rg-ht-bankc-p-cin-01 --name aks-ht-bankc-p-cin-01 --overwrite-existing
```

**PowerShell Multi-Line (Windows):**
```powershell
az aks get-credentials `
  --resource-group rg-ht-bankc-p-cin-01 `
  --name aks-ht-bankc-p-cin-01 `
  --overwrite-existing
```

**Bash / Linux / Azure Cloud Shell Multi-Line:**
```bash
az aks get-credentials \
  --resource-group rg-ht-bankc-p-cin-01 \
  --name aks-ht-bankc-p-cin-01 \
  --overwrite-existing
```
> [!NOTE]
> **PowerShell Line Continuation Syntax:** Windows PowerShell uses the backtick (`` ` ``) for line continuations, whereas Linux/macOS uses the backslash (`\`). Pasting multi-line commands with `\` into PowerShell will fail with `Missing expression after unary operator '--'`. Use the single-line command or backtick syntax in PowerShell.

* **Purpose**: Fetches the `kubeconfig` context and merges it into `~/.kube/config`, configuring Entra ID authentication and cluster API endpoint certificates.
* **When to Use**: Beginning a shift, switching workstations, or after credentials expire.

### 1.2 Connect with Azure RBAC Admin Credentials (Break-Glass Mode)

**Single-Line (PowerShell & Bash):**
```bash
az aks get-credentials --resource-group rg-ht-bankc-p-cin-01 --name aks-ht-bankc-p-cin-01 --admin --overwrite-existing
```

**PowerShell Multi-Line (Windows):**
```powershell
az aks get-credentials `
  --resource-group rg-ht-bankc-p-cin-01 `
  --name aks-ht-bankc-p-cin-01 `
  --admin `
  --overwrite-existing
```

**Bash Multi-Line:**
```bash
az aks get-credentials \
  --resource-group rg-ht-bankc-p-cin-01 \
  --name aks-ht-bankc-p-cin-01 \
  --admin \
  --overwrite-existing
```
* **Purpose**: Bypasses Entra ID interactive browser login and downloads the cluster administrator client certificate.
* **When to Use**: CI/CD automation pipelines or critical incidents when Entra ID conditional access / authentication services are unreachable.

### 1.3 Set Default Namespace to `bank-compliance`
```bash
kubectl config set-context --current --namespace=bank-compliance
```
* **Purpose**: Eliminates the need to append `-n bank-compliance` to every subsequent command, preventing accidental operations in the `default` or `kube-system` namespaces.
* **When to Use**: Directly after connecting to the cluster.

### 1.4 Verify Current Cluster & Active Context
```bash
kubectl config get-contexts
kubectl cluster-info
```
* **Purpose**: Confirms the active Kubernetes context, cluster management endpoint URL, and CoreDNS health.
* **When to Use**: Sanity check before executing modifying commands to ensure you are not targeting the wrong cluster.

---

## 🩺 Tier 2: Real-Time Cluster Health, Node Status & Sizing Headroom

### 2.1 Inspect Node Status & Kubernetes Version
```bash
kubectl get nodes -o wide
```
* **Purpose**: Displays the status (`Ready` vs `NotReady`, `SchedulingDisabled`), OS version, kernel version, internal IP, and container runtime of all nodes.
* **Expected Output**:
  ```text
  NAME                                STATUS   ROLES   AGE   VERSION   INTERNAL-IP   OS-IMAGE
  aks-nodepool1-12345678-vmss000000   Ready    agent   14d   v1.30.9   10.42.0.4     Ubuntu 22.04.5 LTS
  ```

### 2.2 Live CPU & Memory Consumption per Node
```bash
kubectl top nodes
```
* **Purpose**: Queries the Metrics Server to display actual real-time CPU (millicores) and Memory (MiB / GiB) utilization alongside percentage consumption.
* **When to Use**: Diagnosing node throttling or verifying cluster headroom before scheduling high-memory LLM/SLM pods.

### 2.3 Check Node Resource Allocation & Allocatable Headroom
```bash
kubectl describe node -l agentpool=nodepool1 | grep -A 10 "Allocated resources:"
```
* **Purpose**: Displays the exact sum of CPU and Memory **requests** and **limits** committed across all running pods on the node.
* **Platform Engineering Insight**: On a single-node cluster (`Standard_B4ms` with 4 vCPUs / 16GB RAM), if committed CPU requests reach 95-98%, any new pod will stay stuck in `Pending (Insufficient cpu)`.

### 2.4 Discover Unscheduled or Pending Pods Cluster-Wide
```bash
kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded
```
* **Purpose**: Rapidly surfaces any pods across all namespaces that are in `Pending`, `CrashLoopBackOff`, `Error`, or `Unknown` states.
* **When to Use**: Morning health check or post-deployment validation.

---

## 🚀 Tier 3: Pod Lifecycle, Deployments & Rollout Management

### 3.1 Inspect BankCompliance Workload Status
```bash
kubectl get pods -n bank-compliance -o wide
```
* **Purpose**: Lists all pods in the application namespace, their restart counts, age, assigned node, and readiness (`1/1`, `2/2`).
* **Healthy Target State**:
  ```text
  NAME                                      READY   STATUS    RESTARTS   AGE   IP
  bankc-backend-78d4c947bf-k8m9p           1/1     Running   0          4h    10.42.0.15
  bankc-mcp-server-5d66db5d64-x7l2q         1/1     Running   0          4h    10.42.0.18
  litellm-proxy-57c6b4b455-r9w2v            1/1     Running   0          4h    10.42.0.16
  private-slm-inference-658bc94fcb-w4z8n   1/1     Running   0          4h    10.42.0.19
  qdrant-0                                  1/1     Running   0          14d   10.42.0.14
  ```

### 3.2 Trigger Zero-Downtime Rolling Restart
```bash
kubectl rollout restart deployment/bankc-backend -n bank-compliance
```
* **Purpose**: Triggers a graceful rolling update of all backend replicas without changing the image tag, ensuring new pods pass readiness probes before terminating old replicas.
* **When to Use**: Reloading environment variables, refreshing Key Vault mounted secrets, or clearing in-memory state.

### 3.3 Monitor Rollout Progress & Health
```bash
kubectl rollout status deployment/bankc-backend -n bank-compliance --timeout=120s
```
* **Purpose**: Blocks and reports live status until the deployment has successfully created all replicas and passed health checks.
* **When to Use**: In CI/CD deployment scripts or during manual production hotfixes.

### 3.4 Inspect Rollout Revision History
```bash
kubectl rollout history deployment/bankc-backend -n bank-compliance
```
* **Purpose**: Displays the sequential list of rollout revisions (`REVISION 1, 2, 3...`) and the applied changes.
* **When to Use**: Determining which release version is currently live and identifying recent deployment steps.

### 3.5 Immediate Emergency Rollback
```bash
kubectl rollout undo deployment/bankc-backend -n bank-compliance
```
* **Purpose**: Immediately reverts the deployment to the previous known good revision in $< 10$ seconds.
* **When to Use**: Production incident recovery when a new image release causes runtime exceptions or crashes.

---

## 🔍 Tier 4: Live Telemetry, Log Streaming & Deep Diagnostics

### 4.1 Stream Live Application Logs (FastAPI Backend)
```bash
kubectl logs -n bank-compliance -l app=bankc-backend -f --tail=100
```
* **Purpose**: Streams real-time HTTP requests, DPDP PII redaction events, and LangGraph agent execution traces from the active backend pod.
* **When to Use**: Investigating real-time user query errors, 500 responses, or latency anomalies.

### 4.2 Stream LiteLLM AI Gateway Routing Logs
```bash
kubectl logs -n bank-compliance -l app=litellm-proxy -f --tail=50
```
* **Purpose**: Observes multi-cloud model routing decisions (e.g. Primary Google Gemini 2.0 Flash vs Fallback Azure OpenAI `gpt-5.4-nano`) and verifies token spend/latencies.
* **When to Use**: Checking whether model rate limits are triggering failovers to Azure OpenAI.

### 4.3 Inspect Init Container Logs (Ollama Model Puller)
```bash
kubectl logs -n bank-compliance -l app=private-slm-inference -c init-model-puller
```
* **Purpose**: Inspects the bootstrap initialization container responsible for downloading the `qwen2.5:0.5b` model weights into the shared ephemeral volume.
* **When to Use**: If the `private-slm-inference` pod is stuck in `Init:0/1` or `Init:CrashLoopBackOff`.

### 4.4 Diagnose Pod Termination or Restart Cause (Previous Crash Logs)
```bash
kubectl logs -n bank-compliance <pod-name> --previous --tail=100
```
* **Purpose**: Retrieves the exit logs of a container that terminated or crashed before restarting.
* **When to Use**: Diagnosing Python unhandled exceptions, out-of-memory kills (`OOMKilled`), or startup probe failures.

### 4.5 Inspect Kubernetes Event Stream for a Faulty Pod
```bash
kubectl describe pod <pod-name> -n bank-compliance
```
* **Purpose**: Dumps pod configuration, container state, exit codes, volume mounts, and the **Events table** (showing scheduler errors, image pull failures, probe failures).
* **Key Event Signals**:
  * `FailedScheduling`: Insufficient node CPU or memory.
  * `BackOff`: Pod crashing rapidly after starting (`CrashLoopBackOff`).
  * `FailedMount`: PersistentVolumeClaim binding timeout or CSI driver failure.
  * `Unhealthy`: Liveness or Readiness probe failing HTTP checks.

---

## 🔌 Tier 5: Zero-Trust Port-Forwarding & Local Telemetry

> [!NOTE]
> All services below are internal `ClusterIP` resources. Port-forwarding provides a secure, encrypted tunnel from your local machine through the Kubernetes API server without exposing public IPs or opening firewall ports.

### 5.1 Access Grafana Observability Dashboard
```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```
* **Purpose**: Maps local port `http://localhost:3000` to the internal Prometheus/Grafana service.
* **When to Use**: Viewing cluster-wide CPU/Memory dashboards, KEDA scaling metrics, and ingress latency graphs.
* **Credentials**: Default user `admin`, password retrieved via Key Vault or reset dynamically.

### 5.2 Access Qdrant Vector DB Web Console & REST API
```bash
kubectl port-forward svc/qdrant 6333:6333 -n bank-compliance
```
* **Purpose**: Exposes the Qdrant vector search engine UI and API at `http://localhost:6333/dashboard`.
* **When to Use**: Inspecting vector collection health, vector point counts, payload metadata for RBI circulars, and HNSW index memory usage.

### 5.3 Access LiteLLM Proxy Management Interface
```bash
kubectl port-forward svc/litellm-proxy 4000:4000 -n bank-compliance
```
* **Purpose**: Exposes the LiteLLM proxy at `http://localhost:4000`.
* **When to Use**: Testing model routing directly via `curl http://localhost:4000/v1/models` or inspecting active API keys and spend counters.

### 5.4 Test FastMCP Server SSE / Health Endpoint
```bash
kubectl port-forward svc/bankc-mcp-server 8080:8080 -n bank-compliance
```
* **Purpose**: Exposes the FastMCP Model Context Protocol server at `http://localhost:8080/sse`.
* **When to Use**: Validating external AI tool connections and regulatory retrieval tools.

### 5.5 Interactive In-Pod Debugging Shell
```bash
kubectl exec -it deployment/bankc-backend -n bank-compliance -- /bin/bash
```
* **Purpose**: Spawns an interactive bash shell inside the active running container.
* **When to Use**: Validating environment variables, testing internal network reachability (`curl http://qdrant:6333/readyz`), or inspecting bundled statutory markdown files in `/app/documents`.

---

## 📦 Tier 6: Helm Release Management & Stuck State Recovery

### 6.1 List Active Helm Releases
```bash
helm list -n bank-compliance -a
```
* **Purpose**: Displays the release name, revision number, last updated timestamp, chart version, and current deployment status (`deployed`, `failed`, `pending-upgrade`).

### 6.2 Inspect Active Helm Values
```bash
helm get values bank-compliance -n bank-compliance
```
* **Purpose**: Dumps the exact runtime override parameters passed to the chart (e.g. image tags, replica counts, feature flags).
* **When to Use**: Verifying that a new configuration setting was successfully applied during the last release.

### 6.3 Recover from Stuck Helm Release (`pending-upgrade` or `pending-install`)
```bash
# Step 1: Identify the stuck secret
kubectl get secret -n bank-compliance -l "owner=helm,name=bank-compliance" --sort-by=.metadata.creationTimestamp

# Step 2: Delete the failed/stuck revision secret
kubectl delete secret -l owner=helm,name=bank-compliance,status=failed -n bank-compliance
```
* **Purpose**: Fixes the common Helm error `Error: another operation (install/upgrade/rollback) is in progress`. Deleting the orphan lock secret allows Helm to accept new commands immediately without redeploying from scratch.

### 6.4 Dry-Run Helm Upgrade (Pre-Deployment Validation)
```bash
helm upgrade --install bank-compliance ./app/bank-compliance/chart \
  --namespace bank-compliance \
  --dry-run \
  --debug
```
* **Purpose**: Synthesizes all YAML manifests locally and validates them against the Kubernetes API server without applying any changes.
* **When to Use**: Validating templating syntax before merging code to `main`.

---

## 💰 Tier 7: FinOps, Autoscaling & Resource Scaling Controls

### 7.1 Emergency Scale-to-Zero for Non-Essential Workloads
```bash
kubectl scale deployment/vllm-benchmark-inference --replicas=0 -n bank-compliance
```
* **Purpose**: Immediately terminates GPU/heavy inference benchmark pods, freeing up CPU and Memory resources on the cluster while retaining the deployment manifest.
* **When to Use**: Preventing pending scheduling conflicts on single-node clusters or stopping non-production workloads.

### 7.2 Inspect KEDA ScaledObjects & Trigger Health
```bash
kubectl get scaledobject -n bank-compliance
kubectl describe scaledobject bankc-backend-scaler -n bank-compliance
```
* **Purpose**: Checks the status of Kubernetes Event-driven Autoscaling (KEDA), active triggers (Prometheus QPS, Azure Queue depth), and whether the deployment is actively scaling to zero or scaling out.

### 7.3 View Horizontal Pod Autoscalers (HPA)
```bash
kubectl get hpa -n bank-compliance
```
* **Purpose**: Shows current CPU/Memory target thresholds versus live consumption across all autoscaled deployments.

---

## 🔑 Tier 8: Secrets, ConfigMaps & Dynamic Storage Invalidation

### 8.1 Safely Inspect Secret Keys (Without Plaintext Leaks)
```bash
kubectl get secret litellm-secrets -n bank-compliance -o jsonpath='{.data}' | jq 'keys'
```
* **Purpose**: Lists all secret keys present in the secret (e.g. `AZURE_OPENAI_API_KEY`, `GEMINI_API_KEY`) without printing sensitive values to the terminal.

### 8.2 Decode a Specific Secret Value for Verification
```bash
kubectl get secret litellm-secrets -n bank-compliance -o jsonpath="{.data.OPENAI_API_BASE}" | base64 --decode
echo ""
```
* **Purpose**: Extracts and base64-decodes a single secret value for validation against Azure Key Vault.

### 8.3 Invalidate In-Cluster Semantic Vector Cache via REST
```bash
kubectl exec -it deployment/bankc-backend -n bank-compliance -- \
  curl -X POST http://localhost:8000/api/v1/compliance/cache/invalidate
```
* **Purpose**: Clears in-memory Euclidean semantic vector cache entries and invalidates Qdrant collection hash points.
* **When to Use**: Immediately after ingesting a newly gazetted RBI Master Direction or updating statutory circular text.

### 8.4 Check PersistentVolumeClaims (PVC) Status
```bash
kubectl get pvc -n bank-compliance
```
* **Purpose**: Confirms that the Qdrant 4GB CSI disk (`managed-csi`) is in `Bound` state and attached to the node volume.
* **When to Use**: If the `qdrant-0` pod fails to start with `ContainerCreating` or storage mount timeouts.

---

## 🌐 Tier 9: Kubernetes Networking & Ingress Diagnostics

### 9.1 Inspect Ingress Routing Rules & Public DNS
```bash
kubectl get ingress -n bank-compliance
```
* **Purpose**: Verifies that the Ingress resource is bound to the NGINX ingress class and routing traffic for `bank.mytaxbot.site`.

### 9.2 Stream Ingress-NGINX Access & Routing Logs
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -f --tail=50
```
* **Purpose**: Displays client IP addresses, HTTP status codes (`200`, `403`, `502`), upstream latency, and SSL handshake results.
* **When to Use**: Diagnosing `502 Bad Gateway` errors to confirm whether the ingress controller can reach the `bankc-backend` Service.

### 9.3 In-Cluster DNS Resolution Diagnostic
```bash
kubectl run dns-test --rm -it --image=curlimages/curl --restart=Never -- nslookup qdrant.bank-compliance.svc.cluster.local
```
* **Purpose**: Spawns a temporary lightweight pod that queries CoreDNS for internal service resolution and automatically cleans itself up.
* **When to Use**: If backend pods log `Cannot connect to host qdrant:6333 (Name or service not known)`.

---

## 🚨 Tier 10: Production Emergency Checklist (5-Minute Triage)

When a production alert fires for `bank.mytaxbot.site`:

```text
STEP 1: Check Pod Health
$ kubectl get pods -n bank-compliance -o wide
-> Look for RESTARTS > 5, CrashLoopBackOff, or OOMKilled.

STEP 2: Check Node Headroom
$ kubectl top nodes
-> If CPU > 95%, scale down idle workloads:
   $ kubectl scale deploy/vllm-benchmark-inference --replicas=0 -n bank-compliance

STEP 3: Check Backend Error Logs
$ kubectl logs -n bank-compliance -l app=bankc-backend --tail=100
-> Look for uncaught exceptions, LiteLLM gateway timeouts, or Qdrant connection resets.

STEP 4: Check LiteLLM AI Fallback Status
$ kubectl logs -n bank-compliance -l app=litellm-proxy --tail=50
-> Check if primary Gemini rate limit triggered seamless fallback to Azure OpenAI.

STEP 5: Quick Rollback if Recent Deployment
$ kubectl rollout undo deployment/bankc-backend -n bank-compliance
```

---

*Authored by HappyTechies AI Platform Engineering Team | Azure AI Landing Zone CAF Standards*
