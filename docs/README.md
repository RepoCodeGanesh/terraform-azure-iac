# 📚 Azure AI Landing Zone Documentation Hub

Welcome to the **Enterprise Azure AI Landing Zone** documentation repository. This directory contains architectural specifications, subscription maps, CI/CD branching & SemVer guides, and operational runbooks for **TaxBot India** and **BankCompliance AI**.

---

## 🧭 Master Navigation Map

### 1. 🏗️ Architecture & Single Source of Truth
* **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)**: **The primary repository source of truth**. Contains subscription IDs, Entra ID app registrations, dual CI/CD auth mappings (WIF), network CIDR subnets, cost optimization matrix, and multi-root Terraform state rules.
* **[ROADMAP.md](../ROADMAP.md)**: Master 10-phase delivery roadmap (Phases 1–10 Complete).
* **[Confluence Documentation Suite](confluence/README.md)**: Published 12-document enterprise engineering suite on [HappyTechies Atlassian Confluence](https://happytechies.atlassian.net/wiki/spaces/HT/overview).
* **[Platform Guide Visual Suite](platform-guide/README.md)**: Complete 12-module operational runbook suite with interactive Mermaid architecture diagrams.

---

### 2. 🔄 CI/CD, Governance & Observability (`docs/workflows-and-governance/`)
* **[Workflows & Governance Index](workflows-and-governance/README.md)**: Directory overview and standards guide.
* **[BRANCHING_STRATEGY.md](workflows-and-governance/BRANCHING_STRATEGY.md)**: Git branching strategy (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`), pull request merge requirements, and environment deployments.
* **[AUTOMATED_VERSIONING_GUIDE.md](workflows-and-governance/AUTOMATED_VERSIONING_GUIDE.md)**: Automated Semantic Versioning (SemVer) guide via Conventional Commits.
* **[REUSABLE_APP_WORKFLOW_GUIDE.md](workflows-and-governance/REUSABLE_APP_WORKFLOW_GUIDE.md)**: Enterprise Caller/Called Reusable Workflow Pattern guide for GitHub Actions applications.
* **[AKS_HYBRID_OBSERVABILITY_GUIDE.md](workflows-and-governance/AKS_HYBRID_OBSERVABILITY_GUIDE.md)**: Prometheus & Grafana 6-pillar GenAIOps observability guide with native Azure Container Insights.
* **[BankCompliance Troubleshooting & Learnings](confluence/11-bank-compliance-troubleshooting-learnings.md)**: Authoritative 12-issue engineering learnings, root causes, and solutions for AKS, APIM, LiteLLM, and Static Web Apps.

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
| **[12-fine-tuning-and-private-slm-guide.md](platform-guide/12-fine-tuning-and-private-slm-guide.md)** | **PEFT/LoRA Fine-Tuning, Sovereign In-Cluster SLMs & Decoupled MLOps Architecture Runbook**. |

---

### 4. 📦 Milestone Archives (`docs/archive/`)

Historical blueprints and completed milestone execution plans:
* **[Archive Catalog](archive/README.md)**: Overview of archived execution specifications.
* **[Phase 9: Banking Compliance AI Plan](archive/BANKING_COMPLIANCE_AI_PLAN.md)**: Initial AKS workload blueprint.
* **[Phase 10: Regulatory Ingestion & Viewer Plan](archive/RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md)**: Split-screen PDF viewer & CI/CD quality gate blueprint.
* **[BankCompliance Standalone App Guide](archive/BANK_COMPLIANCE_APP_STANDALONE_GUIDE.md)**: Standalone decoupled repository guide.

---

### 5. 🧱 Component-Level Technical Documentation

* **[Platform Infrastructure README](../platform/README.md)**: `platform/bootstrap`, `platform/hub`, and `platform/shared-services` Terraform roots.
* **[Workloads Infrastructure README](../workloads/README.md)**: `workloads/tax-advisor` & `workloads/bank-compliance-ai-aks` specifications.
* **[TaxBot Application README](../app/tax-advisor/README.md)**: TaxBot India React SPA + Python Functions.
* **[BankCompliance Application README](../app/bank-compliance/README.md)**: BankCompliance AI React SPA + FastAPI + Helm + Eval Harness.
* **[Azure DevOps Pipelines README](../pipelines/README.md)**: Azure DevOps pipeline YAML specifications.
