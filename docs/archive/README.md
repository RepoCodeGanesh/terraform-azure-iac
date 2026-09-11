# 📦 Completed Milestones & Architectural Archives

[← Back to Master Documentation Hub](../README.md)

This directory preserves historical architecture blueprints, decoupled repository guides, and completed phase implementation plans. These documents serve as an immutable engineering audit trail for decisions made during earlier delivery cycles.

---

## 📑 Archive Inventory

| Historical Document | Milestone / Phase | Scope & Description | Current Production Location |
| :--- | :---: | :--- | :--- |
| **[BANKING_COMPLIANCE_AI_PLAN.md](BANKING_COMPLIANCE_AI_PLAN.md)** | **Phase 9** | Initial architecture and implementation plan for BankCompliance AI on AKS. *Note: Describes earlier decoupled 2-repo model prior to monorepo consolidation.* | [`workloads/bank-compliance-ai-aks/`](../../workloads/bank-compliance-ai-aks/) & [`app/bank-compliance/`](../../app/bank-compliance/) |
| **[BANK_COMPLIANCE_APP_STANDALONE_GUIDE.md](BANK_COMPLIANCE_APP_STANDALONE_GUIDE.md)** | **Phase 9** | Standalone application guide for `bank-compliance-ai-app`. Retained for decoupled architecture reference. | [`app/bank-compliance/README.md`](../../app/bank-compliance/README.md) |
| **[RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md](RAW_REGULATORY_INGESTION_AND_VIEWER_PLAN.md)** | **Phase 10** | Enterprise Auditable Document Intelligence, Split-Screen PDF Viewer, and CI/CD LLMOps Quality Gates blueprint (**Status: ✅ COMPLETED**). | Live in production on [bank.mytaxbot.site](https://bank.mytaxbot.site) |

---

> [!NOTE]
> For active production runtime specifications, infrastructure topologies, and live endpoints, always refer to the canonical source of truth in **[`docs/PROJECT_CONTEXT.md`](../PROJECT_CONTEXT.md)** and the **[Confluence Suite](../confluence/README.md)**.
