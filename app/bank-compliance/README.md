BankCompliance AI (`bank-compliance-ai-app`)

An Enterprise Cloud-Native Banking Regulatory & Compliance Copilot built on **Azure Kubernetes Service (AKS)** and **Azure OpenAI**, powered by **LiteLLM Gateway**, **Qdrant Vector DB**, and **Azure AI Content Safety**.

Live Domain: **[https://bank.mytaxbot.site](https://bank.mytaxbot.site)**

---

## ðŸ—‚ï¸ Sibling Repository Architecture

This application is decoupled from the cloud platform infrastructure according to Microsoft Cloud Adoption Framework (CAF) practices:

```
c:\Users\RichT\OneDrive\Documents\Repos\
â”œâ”€â”€ terraform-azure-iac/       # Infrastructure repository (Landing Zone, AKS, Hub/Spoke, WIF)
â””â”€â”€ bank-compliance-ai-app/    # Application repository (FastAPI, React SPA, Helm, LiteLLM, Qdrant)
```

* **Infrastructure Repository:** [`terraform-azure-iac`](https://github.com/RepoCodeGanesh/terraform-azure-iac) âž” [`workloads/bank-compliance-ai-aks`](https://github.com/RepoCodeGanesh/terraform-azure-iac/tree/main/workloads/bank-compliance-ai-aks) (Local: `c:\Users\RichT\OneDrive\Documents\Repos\terraform-azure-iac`)
* **Application Repository:** [`bank-compliance-ai-app`](https://github.com/RepoCodeGanesh/bank-compliance-ai-app) (Local: `c:\Users\RichT\OneDrive\Documents\Repos\bank-compliance-ai-app`)

---

### Quick Start (Local Development)

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

---

## ðŸ›ï¸ Infrastructure & Cloud Resources
All cloud infrastructure is provisioned in Azure via Terraform in [`terraform-azure-iac/workloads/bank-compliance-ai-aks`](https://github.com/RepoCodeGanesh/terraform-azure-iac/tree/main/workloads/bank-compliance-ai-aks).