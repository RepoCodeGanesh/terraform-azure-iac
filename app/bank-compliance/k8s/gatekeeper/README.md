# OPA Gatekeeper — G1 Governance Hardening
## BankCompliance AI | `bank-compliance` namespace

Platform-enforced admission control policies using **OPA Gatekeeper** (already live via `azure_policy_enabled = true` on AKS).

---

## Architecture

```
kubectl apply -f bad-pod.yaml
        ↓
┌─────────────────────────┐
│  Kubernetes API Server  │
│  Validating Webhook ────┼──→ Gatekeeper (kube-system)
│                         │         ↓
│                         │   ConstraintTemplate (Rego law)
│                         │         ↓
│                         │   Constraint (jurisdiction)
│                         │         ↓
│                         │   warn / deny
└─────────────────────────┘
```

---

## Files

| File | Kind | Purpose |
|:---|:---|:---|
| `ct-require-nonroot.yaml` | ConstraintTemplate | Rego law: every container must set `runAsNonRoot: true` |
| `constraint-nonroot-bankc.yaml` | K8sRequireNonRoot | Enforce in `bank-compliance` ns, `warn` mode |
| `ct-allowed-registries.yaml` | ConstraintTemplate | Rego law: images must come from approved registries |
| `constraint-registries-bankc.yaml` | K8sAllowedRegistries | Enforce in `bank-compliance` ns, `warn` mode |

---

## Apply Order (templates before constraints)

```bash
# 1. Apply ConstraintTemplates — creates the CRD kinds
kubectl apply -f k8s/gatekeeper/ct-require-nonroot.yaml
kubectl apply -f k8s/gatekeeper/ct-allowed-registries.yaml

# 2. Wait for CRDs to register (~10-15 seconds)
kubectl get constrainttemplates

# 3. Apply Constraints — enforces the policies
kubectl apply -f k8s/gatekeeper/constraint-nonroot-bankc.yaml
kubectl apply -f k8s/gatekeeper/constraint-registries-bankc.yaml

# 4. Verify
kubectl get k8srequirenonroot
kubectl get k8sallowedregistries
```

---

## Check Violations (warn mode — nothing is blocked)

```bash
# See if any existing pods violate the nonroot policy
kubectl get k8srequirenonroot require-nonroot-bank-compliance -o yaml

# See if any images are from unapproved registries
kubectl get k8sallowedregistries allowed-registries-bank-compliance -o yaml

# Verbose view with violation messages
kubectl describe k8srequirenonroot require-nonroot-bank-compliance
kubectl describe k8sallowedregistries allowed-registries-bank-compliance
```

---

## Upgrade to Deny (after zero violations confirmed)

```yaml
# In both constraint files, change:
enforcementAction: warn
# to:
enforcementAction: deny
```

Then re-apply. Future non-compliant pod submissions will be **rejected at the API server** before any resource is created.

---

## Approved Registries

| Registry | Used by |
|:---|:---|
| `ghcr.io` | Backend CI image + LiteLLM |
| `docker.io/qdrant` | Qdrant vector database |
| `docker.io/ollama` | Ollama sovereign SLM |
| `mcr.microsoft.com` | Microsoft init containers |

---

## Interview Talking Points

- *"Gatekeeper enforces our CIS Kubernetes Benchmark controls at admission — before any pod is scheduled, not after"*
- *"We started with `warn` mode to audit our baseline, then hardened to `deny` once we confirmed zero violations"*
- *"ConstraintTemplates are the law written in Rego; Constraints are the jurisdiction — this separation lets us reuse one policy across multiple namespaces with different parameters"*
- *"Our `runAsNonRoot` and approved registry policies close CIS 5.2.6 and 5.5.1 automatically — no runbook, no manual review"*
