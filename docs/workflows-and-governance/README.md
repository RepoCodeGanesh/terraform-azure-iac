# ⚙️ Workflows, Governance & SRE Observability

[← Back to Master Documentation Hub](../README.md)

This directory contains the operational runbooks and engineering specifications governing Git collaboration, CI/CD pipeline automation, automated semantic versioning, and cluster observability for the enterprise Azure AI Landing Zone.

---

## 📑 Governance & Operations Catalog

| Specification Document | Topic & Scope | Primary Implementations |
| :--- | :--- | :--- |
| **[BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md)** | **Enterprise GitFlow & PR Governance** | Branching model (`main`, `develop`, `feature/*`, `release/*`), merge requirements, and CI/CD triggers. |
| **[AUTOMATED_VERSIONING_GUIDE.md](AUTOMATED_VERSIONING_GUIDE.md)** | **Semantic Versioning (SemVer)** | Automated Git tag calculation (`vX.Y.Z`) via Conventional Commits and automated GitHub release generation. |
| **[REUSABLE_APP_WORKFLOW_GUIDE.md](REUSABLE_APP_WORKFLOW_GUIDE.md)** | **Caller/Called Reusable Workflows** | Decoupled 4-stage GitHub Actions architecture (`app-sec-scan`, parallel deploy/sync, CORS config, and SemVer release). |
| **[AKS_HYBRID_OBSERVABILITY_GUIDE.md](AKS_HYBRID_OBSERVABILITY_GUIDE.md)** | **AKS Hybrid Observability** | Azure Container Insights (native KQL) + self-hosted Prometheus & Grafana (6-pillar GenAIOps metrics) at near-zero cost. |

---

## 🧭 Cross-References & Integrations
* For central CI/CD authentication and Entra ID Workload Identity Federation (WIF), see **[`docs/confluence/05-cicd-wif-operations-runbook.md`](../confluence/05-cicd-wif-operations-runbook.md)**.
* For enterprise Log Analytics queries and telemetry architecture, see **[`docs/platform-guide/07-monitoring-telemetry-guide.md`](../platform-guide/07-monitoring-telemetry-guide.md)**.
