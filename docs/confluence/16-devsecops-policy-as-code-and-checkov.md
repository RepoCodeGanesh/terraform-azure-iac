# 16. DevSecOps, Policy-as-Code & Checkov Security Framework

## 1. Metadata & Governance
* **Document ID:** SPEC-SEC-016
* **Architecture Tier:** Identity, Security & Zero-Trust Governance
* **Author / Tech Lead:** Enterprise DevSecOps Team
* **Source Path:** `docs/confluence/16-devsecops-policy-as-code-and-checkov.md`
* **Tooling:** Checkov (Bridgecrew), Trivy (Aqua Security), Azure Policy, CodeQL
* **Status:** Approved / Production-Hardened

---

## 2. DevSecOps Philosophy: "Shift-Left" Security
In the HappyTechies Cloud & AI Platform monorepo, security is an automated, continuous gate rather than an afterthought. Every Terraform line, Kubernetes manifest, and Docker container is analyzed for vulnerabilities **before** merging into the codebase.

```
[ Developer Commit ] ➔ [ Pre-Commit Hooks ] ➔ [ CI/CD Pull Request ] ➔ [ Automated Gate ] ➔ [ Cloud Deploy ]
                             │                         │                       │
                             ▼                         ▼                       ▼
                       Checkov Static           Trivy Container        SARIF Upload &
                       Analysis (IaC)           Vulnerability Scan     PR Block on High
```

---

## 3. Central Checkov Configuration (`.checkov.yaml`)

Checkov is configured at the root of the repository to analyze both Terraform and Kubernetes manifests simultaneously:

```yaml
# .checkov.yaml - Central Monorepo Configuration
framework:
  - terraform
  - kubernetes

output:
  - cli
  - sarif

output-file-path:
  - console
  - checkov-results.sarif

soft-fail: true # Transitioning to false for PR blocking gates
download-external-modules: true
evaluate-variables: true
```

### 3-Phase Enterprise Rollout Strategy:
1. **Phase 1: Discovery (Advisory Mode - Week 1):**
   * Scans run on all platform and workload PRs with `soft_fail: true`.
   * Formatted Markdown tables are published to `$GITHUB_STEP_SUMMARY`.
   * Findings uploaded to GitHub Security tab without blocking developer velocity.
2. **Phase 2: Baselining & Architectural Waivers (Week 2):**
   * Legitimate architectural trade-offs (e.g. Free Tier SKUs lacking dedicated private endpoints, Ephemeral OS disks) are formally documented and baselined.
3. **Phase 3: Automated Enforcement (Week 3+):**
   * `soft_fail: false` enforced for any new `CRITICAL` or `HIGH` severity violations.

---

## 4. Standard Inline Suppression Policy (Waivers)

When an accepted architectural constraint or cost-optimization violates a default security check, engineers must provide a structured justification inline:

```hcl
# checkov:skip=CKV_AZURE_109: "FinOps Constraint: AKS Free Tier does not support multi-tenant dedicated egress gateway."
# checkov:skip=CKV_AZURE_115: "Static Web Apps use managed certificates; custom TLS cert binding not applicable."
resource "azurerm_kubernetes_cluster" "this" {
  ...
}
```

> [!CAUTION]
> Blanket skips without a documented rationale or reference to an Architectural Decision Record (ADR) will be automatically rejected during PR code review.

---

## 5. Container Image Vulnerability Scanning (Trivy)

All Docker images built for the platform (`bankc-backend`, `bankc-mcp-server`, `private-slm-inference`) undergo automated static container scanning before pushing to GitHub Container Registry (GHCR):

```yaml
- name: Scan Docker Image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/${{ github.repository }}/bankc-backend:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '0' # Advisory in PR, blocking on main
```

---

## 6. Azure Policy-as-Code (Enterprise Management Group Enforcement)

At the root Management Group level (`HappieTechies-root-MG`), Azure Policy definitions enforce organizational guardrails declaratively via `platform/governance/`:

| Policy Name | Scope | Enforcement Mode | Objective |
| :--- | :--- | :--- | :--- |
| **Allowed Locations** | Root MG | `Deny` | Restricts deployments strictly to `centralindia` and `southindia`. |
| **Require Cost Tags** | Root MG | `Deny` | Blocks provisioning of any resource missing `Environment`, `Project`, and `CostCenter`. |
| **Disallow Classic Resources** | Root MG | `Deny` | Prohibits unmanaged legacy ASM cloud resources. |
| **Enforce HTTPS Only** | Apps MG | `Deny` | Enforces TLS 1.2+ on all Storage Accounts and Function Apps. |
| **Audit Unattached Disks** | Apps MG | `Audit` | FinOps: Flags orphaned managed disks incurring zombie billing. |

---

## 7. Reusable GitHub Actions Security Scan Template

Security scanning is abstracted into a reusable workflow (`.github/workflows/reusable-checkov-scan.yml`) callable by all workload and platform pipelines:

### Permission Delegation (Incident Learning #16):
When calling the reusable scan workflow, caller workflows must explicitly grant:
```yaml
permissions:
  contents: read
  security-events: write # Required for SARIF upload
  actions: read          # Required for CodeQL action runner delegation
  id-token: write        # Required for OIDC
```
This prevents workflow failures where called actions default to `actions: none`.
