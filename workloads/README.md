# 🚀 Workloads Layer Plan & Architecture

The **Workloads Layer** contains application-specific landing zone spokes. Each workload operates within its own isolated spoke VNet and consumes shared platform services provided by the `platform` layer.

---

## 🎯 Layer Responsibility

- **AI Workload Isolation**: Deploy application-specific Azure OpenAI endpoints, AI Search vector stores, serverless Functions, and App Service backends.
- **Least Privilege Access**: Use Managed Identities to authenticate to shared Key Vault and APIM endpoints without hardcoding secrets.
- **Cost Guardrails**: Utilize `Free` (F1) search SKUs, `Consumption` functions, and strict TPM quota caps for OpenAI models.

---

## 📁 Active Workload Spokes

- **[`workloads/tax-advisor/`](tax-advisor/)**: Production TaxBot India spoke provisioning Azure OpenAI deployments (`gpt-5.4-nano`), AI Search, Cosmos DB Serverless, Function App backend, and Static Web App ([www.mytaxbot.site](https://www.mytaxbot.site)).
- **[`workloads/bank-compliance-ai-aks/`](bank-compliance-ai-aks/)**: Production BankCompliance AI spoke provisioning Azure Kubernetes Service (AKS Free Tier), Qdrant Vector DB on 4GB CSI persistent disk, LiteLLM Multi-Model Gateway, AI Content Safety (`F0`), and Static Web App ([bank.mytaxbot.site](https://bank.mytaxbot.site)).
