# 📚 Azure AI Landing Zone Documentation Hub

Welcome to the **Enterprise Azure AI Landing Zone** documentation repository. This directory contains architectural specifications, subscription maps, CI/CD branching & SemVer guides, and operational runbooks for **TaxBot India** and **BankCompliance AI**.

---

## 🧭 Master Navigation Map

### 1. 🏗️ Architecture & Single Source of Truth
* **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)**: **The primary repository source of truth**. Contains subscription IDs, Entra ID app registrations, dual CI/CD auth mappings (WIF), network CIDR subnets, cost optimization matrix, and multi-root Terraform state rules.
* **[ROADMAP.md](../ROADMAP.md)**: Master 10-phase delivery roadmap (Phases 1–9 Complete, Phase 10 In-Progress).
* **[Confluence Documentation Suite](confluence/README.md)**: Published enterprise documentation suite on [HappyTechies Atlassian Confluence](https://happytechies.atlassian.net/wiki/spaces/HT/overview).

---

### 2. 🔄 CI/CD, Governance & Workflow Guides
* **[BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md)**: Git branching strategy (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`), pull request merge requirements, and environment deployments.
* **[AUTOMATED_VERSIONING_GUIDE.md](AUTOMATED_VERSIONING_GUIDE.md)**: Automated Semantic Versioning (SemVer) guide via Conventional Commits.
* **[REUSABLE_APP_WORKFLOW_GUIDE.md](REUSABLE_APP_WORKFLOW_GUIDE.md)**: Enterprise Caller/Called Reusable Workflow Pattern guide for GitHub Actions applications.
* **[BANK_COMPLIANCE_TROUBLESHOOTING_AND_LEARNINGS.md](BANK_COMPLIANCE_TROUBLESHOOTING_AND_LEARNINGS.md)**: Comprehensive engineering learnings, root causes, and solutions for AKS, APIM, LiteLLM, and Static Web Apps.
* **[RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md](RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md)**: **Phase 10 Execution Blueprint** (Raw Regulatory Lake, Split-Screen PDF Viewer, and Automated PR RAG Quality Gates).
* **[AKS_HYBRID_OBSERVABILITY_GUIDE.md](AKS_HYBRID_OBSERVABILITY_GUIDE.md)**: Prometheus & Grafana 6-pillar GenAIOps observability guide.

---

### 3. 📘 Platform Operations Runbooks (`docs/platform-guide/`)

Detailed step-by-step operational guides for provisioning and operating the Azure AI Landing Zone:

| Runbook File | Description / Topic |
| :--- | :--- |
| **[01-platform-overview.md](platform-guide/01-platform-overview.md)** | High-level landing zone overview, CAF subscriptions, and component topology. |
| **[02-terraform-iac-guide.md](platform-guide/02-terraform-iac-guide.md)** | Multi-root Terraform workflow, backend state storage (`sthtbootpcin01`), and CLI commands. |
| **[03-cicd-pipelines-guide.md](platform-guide/03-cicd-pipelines-guide.md)** | Azure DevOps & GitHub Actions CI/CD pipelines, OIDC/WIF auth, and pipeline sequence diagrams. |
| **[04-naming-and-standards.md](platform-guide/04-naming-and-standards.md)** | Resource naming conventions (CAF pattern `rg-ht-taxb-p-cin-01`), region codes, and tagging rules. |
| **[05-troubleshooting-guide.md](platform-guide/05-troubleshooting-guide.md)** | Known apply risks, Azure OpenAI quota errors, VNet peering locks, and APIM CORS fixes. |
| **[06-blue-green-deployment-guide.md](platform-guide/06-blue-green-deployment-guide.md)** | Zero-downtime Function App & Static Web App deployment strategies. |
| **[07-monitoring-telemetry-guide.md](platform-guide/07-monitoring-telemetry-guide.md)** | Application Insights, Log Analytics queries, and APIM request rate limiting telemetry. |
| **[08-azure-rag-architectural-patterns.md](platform-guide/08-azure-rag-architectural-patterns.md)** | Master RAG taxonomy, 6 architectures, adoption lifecycle matrix, and architectural decision tree. |
| **[09-multi-cloud-ai-gateway-and-fallback-guide.md](platform-guide/09-multi-cloud-ai-gateway-and-fallback-guide.md)** | Multi-Cloud AI Gateway (Gemini Primary $0 + Azure OpenAI Standby Fallback). |
| **[10-enterprise-ai-engineering-backlog-and-roadmap.md](platform-guide/10-enterprise-ai-engineering-backlog-and-roadmap.md)** | Enterprise AI Platform Engineering Roadmap & Phased Gap Analysis. |
| **[11-enterprise-genai-evaluation-and-testing-framework.md](platform-guide/11-enterprise-genai-evaluation-and-testing-framework.md)** | **Enterprise GenAI Evaluation, Ragas Triad, Golden Benchmarks & Testing Pyramid Runbook**. |
| **[12-fine-tuning-and-private-slm-guide.md](confluence/12-fine-tuning-and-private-slm-guide.md)** | **PEFT/LoRA Fine-Tuning, Sovereign In-Cluster SLMs & Decoupled MLOps Architecture Runbook**. |

---

### 4. 🧱 Component-Level Technical Documentation

* **[Platform Infrastructure README](../platform/README.md)**: `platform/bootstrap`, `platform/hub`, and `platform/shared-services` Terraform roots.
* **[Workloads Infrastructure README](../workloads/README.md)**: `workloads/tax-advisor` & `workloads/bank-compliance-ai-aks` specifications.
* **[TaxBot Application README](../app/tax-advisor/README.md)**: TaxBot India React SPA + Python Functions.
* **[BankCompliance Application README](../app/bank-compliance/README.md)**: BankCompliance AI React SPA + FastAPI + Helm + Eval Harness.
* **[Azure DevOps Pipelines README](../pipelines/README.md)**: Azure DevOps pipeline YAML specifications.

