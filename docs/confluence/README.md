# HappyTechies Confluence Enterprise Technical Documentation Suite

[← Back to Master Documentation Hub](../README.md)

The complete **17-document company-level engineering suite** is live on Atlassian Confluence in your space: **`HappyTechies Cloud & AI Platform` (`HT`)** at **[https://happytechies.atlassian.net/wiki/spaces/HT/overview](https://happytechies.atlassian.net/wiki/spaces/HT/overview)**.

---

## 🏛️ Section 1: Enterprise Cloud, Network & Security Foundation
*Multi-Subscription Landing Zone, Network Traffic Ingress/Egress, Zero-Trust Identity, and Governance Standards.*

| Doc # | Specification Document | Domain & Architecture | Live Atlassian Link |
|:---:|:---|:---|:---:|
| **01** | **[01. Azure AI Landing Zone & Enterprise Copilots Overview](01-space-overview-architecture.md)** | 4-Subscription CAF Model, Management Groups, Remote State Map | [Open Page 01 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10289154) |
| **08** | **[08. Cloud & AI Platform Technical Strategy](08-cloud-platform-technical-strategy.md)** | Multi-Root Terraform Architecture, Monorepo State Isolation | [Open Page 08 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10387465) |
| **09** | **[09. Enterprise Network Topology, Packet Routing & DNS Spec](09-enterprise-network-and-traffic-flow.md)** | Cloudflare Full SSL, APIM Ingress, Azure CNI Overlay, Internal Load Balancing | [Open Page 09 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10321962) |
| **06** | **[06. Enterprise Naming & Tagging Standards Specification](06-enterprise-naming-and-tagging-standards.md)** | CAF Naming Dictionaries, Hyphenated/Compact Rules, Tag Initiatives | [Open Page 06 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10321945) |
| **07** | **[07. Enterprise Security, Zero-Trust Architecture & Governance](07-security-governance-zero-trust.md)** | DPDP Act PII Sanitizer, Azure AI Content Safety, OPA Gatekeeper | [Open Page 07 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10452993) |
| **14** | **[14. Enterprise Identity & Access Management (IAM) & RBAC Security Matrix](14-iam-and-rbac-security-matrix.md)** | WIF OIDC Federation, Control vs Data Plane RBAC, Key Vault Policies | [Open Page 14](14-iam-and-rbac-security-matrix.md) |
| **16** | **[16. DevSecOps, Policy-as-Code & Checkov Security Framework](16-devsecops-policy-as-code-and-checkov.md)** | Checkov Static Analysis, Trivy Container Scans, Azure Policy Deny Rules | [Open Page 16](16-devsecops-policy-as-code-and-checkov.md) |

---

## ⚙️ Section 2: Enterprise CI/CD, FinOps & SRE Post-Mortems
*Zero-Trust WIF OIDC Authentication, 3-Tier Decoupled CI/CD, FinOps Scale-to-Zero, and Master RCA Post-Mortems.*

| Doc # | Specification Document | Domain & Architecture | Live Atlassian Link |
|:---:|:---|:---|:---:|
| **05** | **[05. Dual CI/CD, Workload Identity (WIF) & Operations Runbook](05-cicd-wif-operations-runbook.md)** | Entra ID WIF OIDC Exchange, 3-Tier Decoupled CI/CD, Caller/Called Pattern | [Open Page 05 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10420225) |
| **04** | **[04. FinOps & Near-Zero Idle Cost Strategy](04-finops-and-zero-cost-strategy.md)** | Master Cost Matrix ($0.00 Idle), Ephemeral OS, KEDA Scale-to-Zero | [Open Page 04 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10321929) |
| **10** | **[10. Master Incident Post-Mortems & Root Cause Analysis (RCA)](10-incident-post-mortems-and-rca-knowledge-base.md)** | 26 Production SRE Incident Post-Mortems (5-Whys, Diffs, KQL Queries) | [Open Page 10 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10387482) |
| **11** | **[11. BankCompliance AI: Engineering Learnings & Troubleshooting](11-bank-compliance-troubleshooting-learnings.md)** | 12 Production Issues (AKS, APIM URL Rewriting, LiteLLM, CSI Locks) | [Open Page 11 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10485761) |
| **13** | **[13. Enterprise Kubernetes Daily Operations Runbook](13-kubernetes-daily-operations-runbook.md)** | AKS Daily `kubectl`/`helm` commands with purpose & 10 triage tiers | [Open Page 13 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/16908289) |
| **17** | **[17. Centralized Observability, Azure Monitor Workbooks & Telemetry Catalog](17-central-observability-workbooks-and-metrics.md)** | Central LAW, Azure Monitor Workbooks KQL, Diagnostic Streaming | [Open Page 17](17-central-observability-workbooks-and-metrics.md) |

---

## 🤖 Section 3: Enterprise AI Workloads, MLOps & Sovereign Inference
*Production Copilots, 4-Microagent State Machine, LoRA Fine-Tuning Engine, and In-Cluster Sovereign SLM.*

| Doc # | Specification Document | Domain & Architecture | Live Atlassian Link |
|:---:|:---|:---|:---:|
| **02** | **[02. Workload 1: TaxBot India (Serverless PaaS Architecture)](02-workload-taxbot-india.md)** | Function App Y1 + OpenAI `gpt-5.4-nano` + AI Search + Cosmos DB on [mytaxbot.site](https://www.mytaxbot.site) | [Open Page 02 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/7602371) |
| **03** | **[03. Workload 2: BankCompliance AI (Cloud-Native AKS Copilot)](03-workload-bank-compliance-aks.md)** | AKS Free Tier + Qdrant 4GB CSI + LiteLLM Gateway on [bank.mytaxbot.site](https://bank.mytaxbot.site) | [Open Page 03 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/7700481) |
| **12** | **[12. Parameter-Efficient Fine-Tuning (LoRA), Sovereign SLMs & GenAIOps](12-fine-tuning-and-private-slm-guide.md)** | LoRA SFT Training Engine, In-Cluster Sovereign SLM (CPU), RAG vs LoRA Matrix | [Open Page 12 (Live)](https://happytechies.atlassian.net/wiki/spaces/HT/pages/10420242) |
| **15** | **[15. Enterprise C4 Architecture & End-to-End Data Flows](15-enterprise-c4-architecture-and-data-flows.md)** | C4 Context, Container, Component Diagrams & Sequence Data Paths | [Open Page 15](15-enterprise-c4-architecture-and-data-flows.md) |

---

## 🔄 Confluence Synchronization Pipeline

To validate all local Markdown specifications:
```bash
python scripts/sync_to_confluence.py --dry-run
```

To publish specifications to live Atlassian Confluence Cloud Space `[HT]`:
```bash
python scripts/sync_to_confluence.py
```
* **Automated CI/CD:** GitHub Actions `.github/workflows/sync-confluence-docs.yml` automatically validates and synchronizes documentation on every push to `main`.
* **Authentication:** Automatic via Azure Key Vault (`confluence-api-token` in `kv-ht-ss-p-cin-01`) or `CONFLUENCE_API_TOKEN` environment variable.
* **Encoding:** All files are encoded in **UTF-8 without BOM** to guarantee flawless XHTML translation and zero special character corruption.
