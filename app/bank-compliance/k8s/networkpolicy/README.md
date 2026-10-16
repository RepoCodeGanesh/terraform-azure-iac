# Zero-Trust East-West NetworkPolicy Hardening (S2 Architecture)
## BankCompliance AI | `bank-compliance` namespace

Production-grade **Kubernetes NetworkPolicy** implementation enforcing microsegmentation and East-West Zero-Trust traffic control across the BankCompliance AI platform.

---

## 1. Threat Model & Strategic Rationale

In a default Kubernetes cluster, network routing is **flat and open**: any pod in any namespace can communicate with any other pod across any port. 

In regulated banking environments (RBI Master Directions on Cyber Security Framework, CIS Benchmark 5.3.2, PCI-DSS Requirement 1.3), flat networks are a critical vulnerability:
1. **Compromised Ingress / SSRF:** If an external attacker exploits a vulnerability in the FastAPI backend, they could pivot horizontally to inspect or dump the persistent vector database (`qdrant:6333`) or abuse LiteLLM credentials.
2. **Data Exfiltration:** An unconstrained pod could establish unauthorized outbound connections to arbitrary IP addresses or command-and-control servers.
3. **Lateral Movement:** Compromised workloads in other namespaces could probe the banking compliance database.

**Zero-Trust Rule:** *Deny all traffic by default, allow exclusively verified and necessary communication paths by port, protocol, and namespace/pod selector.*

---

## 2. Policy Matrix & Architecture Topology

```
                   [ Internet / SWA Client ]
                               │
                               ▼ HTTPS :443
               ┌───────────────────────────────┐
               │    ingress-nginx namespace    │
               │  ingress-nginx-controller:80  │
               └───────────────┬───────────────┘
                               │
       NetworkPolicy: allow-ingress-to-backend (TCP 8000)
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ bank-compliance namespace (Default Deny All Ingress + Egress)          │
│                                                                        │
│                       ┌─────────────────┐                              │
│                       │  bankc-backend  │                              │
│                       │   (FastAPI)     │                              │
│                       └─┬─────────────┬─┘                              │
│                         │             │                                │
│      allow-backend-to-  │             │ allow-backend-to-              │
│      qdrant (6333/6334) │             │ litellm (4000)                 │
│                         ▼             ▼                                │
│                 ┌─────────────┐ ┌───────────────┐                      │
│                 │   qdrant    │ │ litellm-proxy │                      │
│                 │ (Vector DB) │ │  (AI Gateway) │                      │
│                 └─────────────┘ └───────┬───────┘                      │
│                                         │                              │
└─────────────────────────────────────────┼──────────────────────────────┘
                                          │ allow-litellm-external-egress
                                          │ (TCP 443)
                                          ▼
                         ┌─────────────────────────────────┐
                         │   External LLM Providers        │
                         │   - Google Gemini 2.0 Flash     │
                         │   - Groq Cloud (Llama 3.3 70B)  │
                         │   - Azure OpenAI                │
                         └─────────────────────────────────┘
```

| Policy Name | Target Selector | Traffic | Allowed Ports | Source / Destination |
|:---|:---|:---|:---|:---|
| `default-deny-all` | `{}` (All pods) | Ingress + Egress | None | Denies all unmapped traffic |
| `allow-dns-egress` | `{}` (All pods) | Egress | UDP/TCP 53 | CoreDNS / Node-Local DNS |
| `allow-ingress-to-backend` | `app: bankc-backend` | Ingress | TCP 8000, 80 | `ingress-nginx`, `app-routing-system`, `kube-system` |
| `allow-backend-to-qdrant` | `app: bankc-backend`, `app: qdrant` | Bidirectional | TCP 6333, 6334 | `backend` ⇄ `qdrant` |
| `allow-backend-to-litellm` | `app: bankc-backend`, `app: litellm-proxy` | Bidirectional | TCP 4000 | `backend` ⇄ `litellm-proxy` |
| `allow-external-egress` | `app: litellm-proxy`, `app: bankc-backend` | Egress | TCP 443, TCP 80 | External HTTPS APIs (Gemini, Groq, Azure Content Safety, Entra ID) + IMDS (`169.254.169.254:80`) |
| `allow-monitoring-scraping`| `backend`, `litellm`, `qdrant` | Ingress | TCP 8000, 4000, 6333 | `monitoring` & `kube-system` (Prometheus) |

---

## 3. Safe Deployment & Zero-Downtime Guarantee

### The Cluster Lifecycle Trap:
In Azure AKS Terraform (`azurerm_kubernetes_cluster`):
- Modifying `network_profile.network_policy` from `null`/omitted to `azure` or `calico` **triggers cluster destruction and recreation** (`forces new resource`).
- **Antigravity Rule 10:** Never destroy cloud resources out-of-band or trigger unintentional cluster teardown.
- **Solution:** NetworkPolicy manifests are standard Kubernetes API objects (`networking.k8s.io/v1`). They can be deployed and validated declaratively at the application layer without modifying the cluster lifecycle or incurring downtime.

### Atomic Deployment:
Never apply `default-deny-all.yaml` in isolation. If applied alone, it would momentarily sever DNS and backend routing. Always apply the entire directory atomically:

```bash
# Dry-run validation (Zero Risk)
kubectl apply -f app/bank-compliance/k8s/networkpolicy/ --dry-run=server

# Atomic production apply
kubectl apply -f app/bank-compliance/k8s/networkpolicy/
```

Or execute via the automated deployment script:
```bash
bash scripts/deploy-networkpolicies.sh
```

---

## 4. Verification & Testing Playbook

### Test 1: Verify Legitimate Communication (Must Pass)
```bash
# Exec into backend pod and test connectivity to Qdrant
kubectl exec -n bank-compliance deploy/bankc-backend -c backend -- \
  curl -s -o /dev/null -w "%{http_code}\n" http://qdrant:6333/healthz
# Expected output: 200

# Test connectivity from backend to LiteLLM
kubectl exec -n bank-compliance deploy/bankc-backend -c backend -- \
  curl -s -o /dev/null -w "%{http_code}\n" http://litellm:4000/health/liveliness
# Expected output: 200
```

### Test 2: Verify East-West Isolation (Must Fail / Timeout)
```bash
# Spin up an unauthorized test pod in default namespace
kubectl run test-probe --image=curlimages/curl --rm -it --restart=Never -- \
  curl -m 3 http://qdrant.bank-compliance.svc.cluster.local:6333/healthz
# Expected: Connection timed out (56 / 28) — blocked by NetworkPolicy!
```

---

## 5. Staff+ / Lead Interview Talking Points

1. **Defense-in-Depth vs Outer Perimeter:**
   *"Firewalls and NSGs guard North-South ingress, but once an attacker breaches the DMZ, traditional perimeters offer zero resistance. We instituted Kubernetes NetworkPolicies in the `bank-compliance` namespace to establish zero-trust East-West segmentation, guaranteeing that even if the FastAPI backend was exploited, lateral reconnaissance to Qdrant or unauthorized egress is mathematically blocked at the packet layer."*

2. **Atomic Manifest Rollout vs Blackholing:**
   *"A frequent junior mistake when instituting default-deny policies is applying them sequentially. Applying `default-deny-all` before `allow-dns` cuts off CoreDNS resolution cluster-wide, causing instant cascading pod liveness probe failures. We engineered atomic manifest rollouts and scripted validation where DNS, ingress, and egress policies are reconciled simultaneously."*

3. **Terraform Provider Safety:**
   *"When dealing with AKS, modifying `network_policy` in Terraform triggers a complete cluster destroy-recreate cycle. We preserved remote state integrity and zero-downtime operations by deploying declarative application policies directly while managing cluster-level network plugins through controlled maintenance windows."*
