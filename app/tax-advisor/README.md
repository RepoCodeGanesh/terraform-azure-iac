# TaxBot India Application (`app/tax-advisor`)

An Enterprise AI Income Tax & Salary Optimization Copilot for Indian Income Tax FY 2026-27 (AY 2027-28), built on **Azure Serverless PaaS** (Python Linux Function App + Azure OpenAI `gpt-5.4-nano` + Azure AI Search + Azure Cosmos DB + React SPA).

* **Live Production Domain:** **[https://www.mytaxbot.site](https://www.mytaxbot.site)**
* **Infrastructure Root:** [`workloads/tax-advisor/`](../../workloads/tax-advisor/)
* **CI/CD Workflows:** `.github/workflows/app-tax-advisor.yml` & `pipelines/azure-cicd-app-tax-advisor.yml`

---

## 🏛️ Application Architecture

```
app/tax-advisor/
├── backend/            # Python 3.11 Azure Function App (HTTP Trigger API)
│   ├── function_app.py # API routes: /api/tax/chat, /api/tax/calculate, /api/tax/compare
│   ├── services/       # Azure OpenAI, AI Search RAG, Cosmos DB memory
│   └── requirements.txt
├── frontend/           # React 18 SPA (Vite + Tailwind/CSS)
│   ├── src/            # Tax Calculator, Chat Assistant, Regime Comparison
│   ├── package.json
│   └── staticwebapp.config.json # Azure Static Web Apps routing & CORS
└── documents/          # Structured statutory tax corpus (Markdown .md)
    ├── 01-master-regime-comparison-slabs-fy2627.md
    ├── 02-master-deductions-80c-80d-nps-80e-80g.md
    ├── 03-housing-hra-home-loan-benefits.md
    ├── 04-salary-ctc-tax-optimization.md
    ├── 05-capital-gains-equity-property-crypto-fy2627.md
    ├── 06-freelancer-business-44ad-44ada-guide.md
    ├── 07-nri-foreign-income-esop-taxation.md
    ├── 08-senior-citizens-pensioners-tax-guide.md
    ├── 09-itr-form-selection-tds-advance-tax-guide.md
    └── 10-budget-2025-cbdt-circulars-faqs.md
```

---

## 💻 Local Development Quickstart

### 1. Backend (Python Function App)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
func start
```

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

---

## 🛡️ Key Features
1. **Regime Comparison Calculator**: Real-time simulation of New vs. Old Tax Regimes under FY 2026-27 rules.
2. **Statutory RAG System**: Grounds responses using 10 curated Income Tax Act Markdown guides stored in `documents/` and indexed in Azure AI Search.
3. **Session Memory**: Stateful multi-turn tax consultation backed by Azure Cosmos DB Serverless Free Tier.
4. **Prompt Security**: APIM rate limiting and Azure AI Content Safety filters.
