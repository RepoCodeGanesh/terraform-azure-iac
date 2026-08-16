# Project Context & Environment Specifications

This document defines the runtime environment, endpoint connections, and operational configuration for **BankCompliance AI (`bank-compliance-ai-app`)**.

---

## ðŸ—‚ï¸ Local Workspace Layout

```
c:\Users\RichT\OneDrive\Documents\Repos\
â”œâ”€â”€ terraform-azure-iac/       # Infrastructure repository (Landing Zone, AKS IaC)
â””â”€â”€ bank-compliance-ai-app/    # Application repository (FastAPI, React, Helm, KEDA)
```

---

## ðŸŒ Connected Cloud Infrastructure

* **Infrastructure Repository:** [`terraform-azure-iac`](https://github.com/RepoCodeGanesh/terraform-azure-iac) âž” [`workloads/bank-compliance-ai-aks`](https://github.com/RepoCodeGanesh/terraform-azure-iac/tree/main/workloads/bank-compliance-ai-aks)
* **Application Repository:** [`bank-compliance-ai-app`](https://github.com/RepoCodeGanesh/bank-compliance-ai-app)
* **Domain Name:** `https://bank.mytaxbot.site`
* **Static Web App:** `stapp-ht-bankc-p-cin-01`
* **Kubernetes Cluster:** `aks-ht-bankc-p-cin-01` (Resource Group: `rg-ht-bankc-p-cin-01` in Central India)
* **Content Safety:** `https://cs-ht-ss-p-sea-01.cognitiveservices.azure.com/` (Southeast Asia — shared-services)
* **OpenAI Endpoint:** `https://oai-ht-ss-p-eus-01.openai.azure.com/` (East US — shared-services)
* **Model Deployment:** `gpt-5.4-nano` (API Version: `2026-03-17`)
* **APIM Gateway:** `https://apim-ht-ss-p-cin-01.azure-api.net/bankc`

---

## ðŸ›¡ï¸ Security & FinOps Standards

1. **Near-Zero Idle Cost:** Automated `az aks stop` / `az aks start` governance keeps idle compute cost at **$0.00** (~â‚¹25/day active).
2. **Qdrant Storage:** 4GB Azure Managed Disk (`storageClassName: managed-csi`, `E1` tier = ~$0.15/month).
3. **Passwordless Auth:** Azure Workload Identity (OIDC) maps Kubernetes Service Account `bankc-sa` to Managed Identity `uami-ht-bankc-p-cin-01`.
4. **PII Masking Engine:** Auto-redacts Indian PAN cards (`[PAN-REDACTED]`), Aadhaar numbers, and bank account numbers prior to LLM processing.
5. **Zero Data Retention:** Compliant with RBI, DPDP, and banking regulatory standards.