# 🏛️ Platform Layer Plan & Architecture

The **Platform Layer** contains the core shared infrastructure managed by the Central IT / Platform DevOps team. It provides foundational networking, identity, security, API gateway, and telemetry services consumed by all application workloads.

---

## 🎯 Layer Responsibility

- **Central Security & Identity**: Manage root Terraform state storage (`bootstrap`) and Key Vault RBAC access.
- **Connectivity & Networking**: Provision the Hub Virtual Network, subnets, Network Security Groups (NSGs), and Private DNS Zones (`hub`).
- **Shared Platform Services**: Deploy central API Management (`APIM`) for AI Gateway token caching & rate-limiting, and centralized Log Analytics for telemetry (`shared-services`).

---

## 📁 Sub-Component Execution Order

1. `platform/bootstrap/`: Provision remote Terraform state storage account and backend key vault.
2. `platform/hub/`: Provision central Hub Virtual Network and NSG rules.
3. `platform/shared-services/`: Provision APIM AI Gateway (`Consumption_0` SKU) and Log Analytics Workspace.
