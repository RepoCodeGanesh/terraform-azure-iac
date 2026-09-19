# 13. Enterprise Kubernetes Daily Operations Runbook

* **Space:** `HappyTechies Cloud & AI Platform` -> `Runbooks & Operations`
* **Document ID:** `CR-OPS-13`
* **Cluster:** `aks-ht-bankc-p-cin-01` (SKU: `Free`, Region: `Central India`)
* **Resource Group:** `rg-ht-bankc-p-cin-01` (Apps-prod Subscription: `f4ffefe1-d689-4059-969c-ccc73e2a11d4`)
* **Primary Workload:** BankCompliance AI (`bank.mytaxbot.site`)
* **Status:** `PRODUCTION READY & OPERATIONALLY ENFORCED`

---

## Table of Contents
1. [Cluster Topology & Namespace Architecture](#1-cluster-topology--namespace-architecture)
2. [Command Matrix: Quick Reference](#2-command-matrix-quick-reference)
3. [Tier 1: Cluster Access, Context & Entra ID Identity Management](#tier-1-cluster-access-context--entra-id-identity-management)
4. [Tier 2: Real-Time Cluster Health, Node Status & Sizing Headroom](#tier-2-real-time-cluster-health-node-status--sizing-headroom)
5. [Tier 3: Multi-Agent AI Workload & Pod Lifecycle Management](#tier-3-multi-agent-ai-workload--pod-lifecycle-management)
6. [Tier 4: Live Telemetry, Log Streaming & Deep Diagnostics](#tier-4-live-telemetry-log-streaming--deep-diagnostics)
7. [Tier 5: Zero-Trust Port-Forwarding & Local Telemetry](#tier-5-zero-trust-port-forwarding--local-telemetry)
8. [Tier 6: Helm Release Management & Stuck State Recovery](#tier-6-helm-release-management--stuck-state-recovery)
9. [Tier 7: FinOps, Autoscaling & Resource Scaling Controls](#tier-7-finops-autoscaling--resource-scaling-controls)
10. [Tier 8: Secrets, ConfigMaps & Dynamic Storage Invalidation](#tier-8-secrets-configmaps--dynamic-storage-invalidation)
11. [Tier 9: Kubernetes Networking & Ingress Diagnostics](#tier-9-kubernetes-networking--ingress-diagnostics)
12. [Tier 10: 5-Minute Production Emergency Triage Card](#tier-10-5-minute-production-emergency-triage-card)

---

## 1. Cluster Topology & Namespace Architecture

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

## 2. Command Matrix: Quick Reference

| Operational Domain | Primary Target Resources | When to Use | Core Purpose |
|:---|:---|:---|:---|
| **Tier 1: Identity & Access** | `az aks get-credentials`, Contexts | Shift handover, session startup | Authenticate via Entra ID & lock workspace namespace |
| **Tier 2: Cluster Sizing** | Nodes, Metrics Server, Headroom | Morning health check, pre-deploy | Measure live CPU/RAM headroom & detect pending pods |
| **Tier 3: Pod Lifecycle** | Deployments, ReplicaSets, Rollouts | CI/CD promotion, zero-downtime hotfix | Graceful restarts, progressive rollouts & instant rollbacks |
| **Tier 4: Deep Diagnostics** | Multi-container pods, Init containers | Debugging 500s, SLM weight pulls | Live log streaming, tracing PII sanitization & crash analysis |
| **Tier 5: Zero-Trust Debug** | Grafana, Qdrant, LiteLLM, FastMCP | Safe admin access without public IPs | Encrypted tunnel through K8s API server to internal ports |
| **Tier 6: Helm Governance** | Helm releases, orphan secrets | Pipeline failures, upgrade timeouts | Unstick pending releases by clearing dead lock secrets |
| **Tier 7: FinOps Autoscaling** | Replicas, KEDA ScaledObjects | Nightly idle shutdown, cost control | Scale non-essential inference to 0 to eliminate waste |
| **Tier 8: Secrets & Storage** | ConfigMaps, Key Vault secrets, CSI | Secret rotation, circular updates | Audit secret keys and trigger instant vector cache purges |
| **Tier 9: Networking & DNS** | CoreDNS, Ingress-NGINX, Services | Investigating 502/504 errors | Verify ingress proxy routing and internal cluster DNS |
| **Tier 10: Emergency Triage** | Cluster-wide triage flowchart | P1/P0 Production Alert fires | 5-step structured response resolving incidents in <5 min |

---

## Tier 1: Cluster Access, Context & Entra ID Identity Management

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

* **Operational Purpose**: Fetches the cluster credentials from Azure Resource Manager and merges the Entra ID authentication context into local `~/.kube/config`.
* **When to Use**: Beginning a shift, switching workstations, or after Entra ID tokens expire.

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
* **Operational Purpose**: Bypasses Entra ID interactive browser login and downloads the root cluster administrator certificate.
* **When to Use**: Automated headless pipelines or critical incidents when Entra ID conditional access / authentication services are unreachable.

### 1.3 Set Default Namespace to `bank-compliance`
```bash
kubectl config set-context --current --namespace=bank-compliance
```
* **Operational Purpose**: Sets the active Kubernetes context namespace to `bank-compliance`, avoiding the need to append `-n bank-compliance` to every command and preventing accidental operations in `default` or `kube-system`.

### 1.4 Verify Current Cluster & API Endpoint Health
```bash
kubectl config get-contexts
kubectl cluster-info
```
* **Operational Purpose**: Verifies the active context name, cluster management endpoint URL, and CoreDNS health before executing any state-modifying commands.

---

## Tier 2: Real-Time Cluster Health, Node Status & Sizing Headroom

### 2.1 Inspect Node Status & Kubernetes Version
```bash
kubectl get nodes -o wide
```
* **Operational Purpose**: Validates that all node pool VMs report status `Ready`, and inspects OS version, kernel version, internal IP (`10.42.0.4`), and container runtime.
* **Target Output**:
```text
NAME                                STATUS   ROLES   AGE   VERSION   INTERNAL-IP   OS-IMAGE
aks-nodepool1-12345678-vmss000000   Ready    agent   14d   v1.30.9   10.42.0.4     Ubuntu 22.04.5 LTS
```

### 2.2 Live CPU & Memory Consumption per Node
```bash
kubectl top nodes
```
* **Operational Purpose**: Queries the Metrics Server to report real-time CPU (millicores) and Memory (MiB / GiB) utilization along with percentage consumption across the host VM.
* **When to Use**: Investigating node throttling or assessing capacity before running intensive LLM/SLM inference workloads.

### 2.3 Check Node Resource Allocation & Committed Headroom
```bash
kubectl describe node -l agentpool=nodepool1 | grep -A 10 "Allocated resources:"
```
* **Operational Purpose**: Displays the committed sum of CPU and Memory **requests** and **limits** across all running pods on the node.
* **SRE Warning**: On a single-node cluster (`Standard_B4ms` with 4 vCPUs / 16GB RAM), if committed CPU requests reach 95-98%, any new pod will stay stuck in `Pending (Insufficient cpu)`.

### 2.4 Discover Unscheduled or Pending Pods Cluster-Wide
```bash
kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded
```
* **Operational Purpose**: Rapidly surfaces any pods across all namespaces that are in `Pending`, `CrashLoopBackOff`, `Error`, or `Unknown` states.

---

## Tier 3: Multi-Agent AI Workload & Pod Lifecycle Management

### 3.1 Inspect BankCompliance Workload Status
```bash
kubectl get pods -n bank-compliance -o wide
```
* **Operational Purpose**: Lists all application pods, restart counts, age, assigned node IP, and container readiness (`1/1`).
* **Healthy State Target**:
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
* **Operational Purpose**: Performs a graceful rolling update of all backend replicas without changing the image tag, ensuring new pods pass readiness probes before terminating old replicas.
* **When to Use**: Reloading environment variables, refreshing Key Vault mounted secrets, or clearing in-memory state.

### 3.3 Monitor Rollout Progress & Health
```bash
kubectl rollout status deployment/bankc-backend -n bank-compliance --timeout=120s
```
* **Operational Purpose**: Blocks and monitors live status until the deployment finishes creating all replicas and passing health checks.

### 3.4 Inspect Rollout Revision History
```bash
kubectl rollout history deployment/bankc-backend -n bank-compliance
```
* **Operational Purpose**: Displays the sequential list of rollout revisions (`REVISION 1, 2, 3...`) to identify active releases.

### 3.5 Immediate Emergency Rollback
```bash
kubectl rollout undo deployment/bankc-backend -n bank-compliance
```
* **Operational Purpose**: Immediately reverts the deployment to the previous known good revision in $< 10$ seconds during a bad deployment.

---

## Tier 4: Live Telemetry, Log Streaming & Deep Diagnostics

### 4.1 Stream Live Application Logs (FastAPI Backend)
```bash
kubectl logs -n bank-compliance -l app=bankc-backend -f --tail=100
```
* **Operational Purpose**: Streams real-time HTTP requests, DPDP PII redaction events, and LangGraph agent execution traces from the active backend pod.

### 4.2 Stream LiteLLM AI Gateway Routing Logs
```bash
kubectl logs -n bank-compliance -l app=litellm-proxy -f --tail=50
```
* **Operational Purpose**: Observes multi-cloud model routing decisions (Primary Google Gemini 2.0 Flash vs Fallback Azure OpenAI `gpt-5.4-nano`) and verifies token spend/latencies.

### 4.3 Inspect Init Container Logs (Ollama Model Puller)
```bash
kubectl logs -n bank-compliance -l app=private-slm-inference -c init-model-puller
```
* **Operational Purpose**: Inspects the bootstrap initialization container responsible for downloading the `qwen2.5:0.5b` model weights into the shared ephemeral volume.
* **When to Use**: If the `private-slm-inference` pod is stuck in `Init:0/1` or `Init:CrashLoopBackOff`.

### 4.4 Diagnose Pod Termination or Restart Cause (Previous Crash Logs)
```bash
kubectl logs -n bank-compliance <pod-name> --previous --tail=100
```
* **Operational Purpose**: Retrieves the exit logs and stacktrace of a container that terminated or crashed before restarting (`OOMKilled` or unhandled exceptions).

### 4.5 Inspect Kubernetes Event Stream for a Faulty Pod
```bash
kubectl describe pod <pod-name> -n bank-compliance
```
* **Operational Purpose**: Dumps pod configuration, container state, exit codes, volume mounts, and the **Events table** (`FailedScheduling`, `BackOff`, `Unhealthy`).

---

## Tier 5: Zero-Trust Port-Forwarding & Local Telemetry

> **Zero-Trust Rationale**: All services in this cluster are internal `ClusterIP` resources. Port-forwarding provides an encrypted tunnel from your local machine through the Kubernetes API server without exposing public IPs or opening firewall ports.

### 5.1 Access Grafana Observability Dashboard
```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```
* **Operational Purpose**: Maps local port `http://localhost:3000` to the internal Prometheus/Grafana service.
* **When to Use**: Viewing cluster-wide CPU/Memory dashboards, KEDA scaling metrics, and ingress latency graphs.

### 5.2 Access Qdrant Vector DB Web Console & REST API
```bash
kubectl port-forward svc/qdrant 6333:6333 -n bank-compliance
```
* **Operational Purpose**: Exposes the Qdrant vector search engine UI and API at `http://localhost:6333/dashboard`.
* **When to Use**: Inspecting vector collection health, vector point counts, payload metadata for RBI circulars, and HNSW index memory usage.

### 5.3 Access LiteLLM Proxy Management Interface
```bash
kubectl port-forward svc/litellm-proxy 4000:4000 -n bank-compliance
```
* **Operational Purpose**: Exposes the LiteLLM proxy at `http://localhost:4000`.
* **When to Use**: Testing model routing directly via `curl http://localhost:4000/v1/models` or inspecting active API keys and spend counters.

### 5.4 Test FastMCP Server SSE / Health Endpoint
```bash
kubectl port-forward svc/bankc-mcp-server 8080:8080 -n bank-compliance
```
* **Operational Purpose**: Exposes the FastMCP Model Context Protocol server at `http://localhost:8080/sse`.
* **When to Use**: Validating external AI tool connections and regulatory retrieval tools.

### 5.5 Interactive In-Pod Debugging Shell
```bash
kubectl exec -it deployment/bankc-backend -n bank-compliance -- /bin/bash
```
* **Operational Purpose**: Spawns an interactive bash shell inside the active running container to test network reachability (`curl http://qdrant:6333/readyz`) or inspect bundled statutory markdown files in `/app/documents`.

---

## Tier 6: Helm Release Management & Stuck State Recovery

### 6.1 List Active Helm Releases
```bash
helm list -n bank-compliance -a
```
* **Operational Purpose**: Displays the release name, revision number, last updated timestamp, chart version, and current deployment status (`deployed`, `failed`, `pending-upgrade`).

### 6.2 Inspect Active Helm Values
```bash
helm get values bank-compliance -n bank-compliance
```
* **Operational Purpose**: Dumps the exact runtime override parameters passed to the chart (e.g. image tags, replica counts, feature flags).

### 6.3 Recover from Stuck Helm Release (`pending-upgrade` or `pending-install`)
```bash
# Step 1: Identify the stuck secret
kubectl get secret -n bank-compliance -l "owner=helm,name=bank-compliance" --sort-by=.metadata.creationTimestamp

# Step 2: Delete the failed/stuck revision secret
kubectl delete secret -l owner=helm,name=bank-compliance,status=failed -n bank-compliance
```
* **Operational Purpose**: Resolves the common Helm lock error `Error: another operation (install/upgrade/rollback) is in progress`. Deleting the orphan lock secret allows Helm to accept new commands immediately without redeploying from scratch.

### 6.4 Dry-Run Helm Upgrade (Pre-Deployment Validation)
```bash
helm upgrade --install bank-compliance ./app/bank-compliance/chart \
  --namespace bank-compliance \
  --dry-run \
  --debug
```
* **Operational Purpose**: Synthesizes all YAML manifests locally and validates them against the Kubernetes API server without applying changes.

---

## Tier 7: FinOps, Autoscaling & Resource Scaling Controls

### 7.1 Emergency Scale-to-Zero for Non-Essential Workloads
```bash
kubectl scale deployment/vllm-benchmark-inference --replicas=0 -n bank-compliance
```
* **Operational Purpose**: Immediately terminates GPU/heavy inference benchmark pods, freeing up CPU and Memory resources on the cluster while retaining the deployment manifest.

### 7.2 Inspect KEDA ScaledObjects & Trigger Health
```bash
kubectl get scaledobject -n bank-compliance
kubectl describe scaledobject bankc-backend-scaler -n bank-compliance
```
* **Operational Purpose**: Checks the status of Kubernetes Event-driven Autoscaling (KEDA), active triggers (Prometheus QPS, Azure Queue depth), and whether the deployment is actively scaling to zero or scaling out.

### 7.3 View Horizontal Pod Autoscalers (HPA)
```bash
kubectl get hpa -n bank-compliance
```
* **Operational Purpose**: Shows current CPU/Memory target thresholds versus live consumption across all autoscaled deployments.

---

## Tier 8: Secrets, ConfigMaps & Dynamic Storage Invalidation

### 8.1 Safely Inspect Secret Keys (Without Plaintext Leaks)
```bash
kubectl get secret litellm-secrets -n bank-compliance -o jsonpath='{.data}' | jq 'keys'
```
* **Operational Purpose**: Lists all secret keys present in the secret without printing sensitive values to the terminal.

### 8.2 Decode a Specific Secret Value for Verification
```bash
kubectl get secret litellm-secrets -n bank-compliance -o jsonpath="{.data.OPENAI_API_BASE}" | base64 --decode
echo ""
```
* **Operational Purpose**: Extracts and base64-decodes a single secret value for validation against Azure Key Vault.

### 8.3 Invalidate In-Cluster Semantic Vector Cache via REST
```bash
kubectl exec -it deployment/bankc-backend -n bank-compliance -- \
  curl -X POST http://localhost:8000/api/v1/compliance/cache/invalidate
```
* **Operational Purpose**: Clears in-memory Euclidean semantic vector cache entries and invalidates Qdrant collection hash points immediately after ingesting a new RBI circular.

### 8.4 Check PersistentVolumeClaims (PVC) Status
```bash
kubectl get pvc -n bank-compliance
```
* **Operational Purpose**: Confirms that the Qdrant 4GB CSI disk (`managed-csi`) is in `Bound` state and attached to the node volume.

---

## Tier 9: Kubernetes Networking & Ingress Diagnostics

### 9.1 Inspect Ingress Routing Rules & Public DNS
```bash
kubectl get ingress -n bank-compliance
```
* **Operational Purpose**: Verifies that the Ingress resource is bound to the NGINX ingress class and routing traffic for `bank.mytaxbot.site`.

### 9.2 Stream Ingress-NGINX Access & Routing Logs
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -f --tail=50
```
* **Operational Purpose**: Displays client IP addresses, HTTP status codes (`200`, `403`, `502`), upstream latency, and SSL handshake results.

### 9.3 In-Cluster DNS Resolution Diagnostic
```bash
kubectl run dns-test --rm -it --image=curlimages/curl --restart=Never -- nslookup qdrant.bank-compliance.svc.cluster.local
```
* **Operational Purpose**: Spawns a temporary lightweight pod that queries CoreDNS for internal service resolution and automatically cleans itself up.

---

## Tier 10: 5-Minute Production Emergency Triage Card

When a production incident alert triggers for `bank.mytaxbot.site`:

```text
STEP 1: Check Pod Health
$ kubectl get pods -n bank-compliance -o wide
-> Look for RESTARTS > 5, CrashLoopBackOff, or OOMKilled.

STEP 2: Check Node Headroom
$ kubectl top nodes
-> If CPU > 95%, scale down idle non-essential workloads:
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
