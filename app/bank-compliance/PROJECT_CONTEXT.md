# BankCompliance AI — Runtime Context & Environment Specifications

This document defines the runtime environment, endpoint connections, and operational configuration for **BankCompliance AI** hosted in `app/bank-compliance/`.

---

## 📁 Repository Layout & Monorepo Location

* **Application Path:** `app/bank-compliance/`
* **Workload Infrastructure:** `workloads/bank-compliance-ai-aks/`
* **Helm Chart:** `app/bank-compliance/chart/`
* **CI/CD Quality Evaluation:** `app/bank-compliance/eval/`

---

## 🌐 Connected Cloud Infrastructure & Endpoints

* **Live Production Domain:** [https://bank.mytaxbot.site](https://bank.mytaxbot.site)
* **Static Web App:** `stapp-ht-bankc-p-cin-01`
* **Kubernetes Cluster:** `aks-ht-bankc-p-cin-01` (Resource Group: `rg-ht-bankc-p-cin-01` in Central India)
* **AI Content Safety:** `https://cs-ht-ss-p-sea-01.cognitiveservices.azure.com/` (`F0` Free Tier in Southeast Asia)
* **OpenAI Fallback Endpoint:** `https://oai-ht-ss-p-eus-01.openai.azure.com/` (East US — `gpt-5.4-nano`)
* **Primary AI Engine:** Google Gemini 2.0 Flash / Flash-Lite / Thinking (Google AI Studio Free Tier)
* **APIM Gateway Endpoint:** `https://apim-ht-ss-p-cin-01.azure-api.net/bankc`

---

## 🛡️ Security & FinOps Standards

1. **Near-Zero Idle Cost:** Automated `az aks stop` / `az aks start` governance keeps idle compute cost at **$0.00** (~₹25/day active).
2. **Qdrant Storage:** 4GB Azure Managed Disk (`storageClassName: managed-csi`, `E1` tier = ~$0.15/month).
3. **Passwordless Auth:** Azure Workload Identity (OIDC) maps Kubernetes Service Account `bankc-sa` to Managed Identity `uami-ht-bankc-p-cin-01`.
4. **PII Masking Engine:** Auto-redacts Indian PAN cards (`[PAN-REDACTED]`), Aadhaar numbers, and bank account numbers prior to LLM processing.
5. **Governed Semantic Cache:** Qdrant similarity cache serving recurring queries in <10ms at $0 token spend with `corpus_version` invalidation.
6. **Zero Data Retention:** Compliant with RBI, DPDP, and banking regulatory standards.