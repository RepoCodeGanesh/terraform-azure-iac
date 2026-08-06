# 🚀 Workloads Layer Plan & Architecture

The **Workloads Layer** contains application-specific landing zone spokes. Each workload operates within its own isolated spoke VNet and consumes shared platform services provided by the `platform` layer.

---

## 🎯 Layer Responsibility

- **AI Workload Isolation**: Deploy application-specific Azure OpenAI endpoints, AI Search vector stores, serverless Functions, and App Service backends.
- **Least Privilege Access**: Use Managed Identities to authenticate to shared Key Vault and APIM endpoints without hardcoding secrets.
- **Cost Guardrails**: Utilize `Free` (F1) search SKUs, `Consumption` functions, and strict TPM quota caps for OpenAI models.

---

## 📁 Active Workload Spokes

- **`workloads/tax-advisor/`**: Production TaxBot India spoke provisioning Azure OpenAI deployments (`gpt-5.4-nano`), AI Search, Cosmos DB, Function App backend, and Static Web App (`www.mytaxbot.site`).
