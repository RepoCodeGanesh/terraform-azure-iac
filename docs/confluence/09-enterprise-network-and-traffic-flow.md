# Confluence Technical Specification: Enterprise Network Topology, Packet Routing & DNS Architecture

**Document ID:** `CR-NET-09`  
**Classification:** Enterprise Cloud & Network Infrastructure Architecture  
**Target Workload:** HappyTechies Enterprise Landing Zone (All Subscriptions)  
**Status:** `ACTIVE / PRODUCTION`  

---

## 1. Executive Network Overview & Scope

This specification defines the **end-to-end network topology, traffic ingress/egress patterns, IP addressing scheme, DNS resolution, and firewall security policies** for the HappyTechies Cloud & AI Platform.

The architecture follows the **Microsoft Cloud Adoption Framework (CAF) Hub-and-Spoke** network topology:
* **Central Hub Network (`vnet-ht-hub-p-cin-01`):** Hosts shared ingress/egress perimeter services (Azure Firewall, Virtual Network Gateway, Bastion).
* **Workload Spoke 1 (`vnet-ht-taxb-p-cin-01`):** Hosts TaxBot India Serverless PaaS.
* **Workload Spoke 2 (`vnet-ht-bankc-p-cin-01`):** Hosts BankCompliance AI AKS Cluster with Azure CNI Overlay.

---

## 2. Visio-Level Global Ingress & Packet Flow Diagram

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                   GLOBAL EDGE INGRESS, SSL TERMINATION & PACKET ROUTING                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

 [ Client Browser (User / Auditor) ]
        │
        │ 1. DNS Query: bank.mytaxbot.site (HTTPS TCP 443)
        ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ Cloudflare Global Anycast Edge Network (DDoS Layer 7 Shield)              │
 │ • SSL Termination: Full (Strict) TLS 1.3 / TLS 1.2                        │
 │ • Edge Caching: Static Assets (TTL: 86400s), Dynamic API Bypassed         │
 │ • DNS CNAME Flattening: bank.mytaxbot.site ➔ apim-ht-ss-p-cin-01          │
 └─────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       │ 2. HTTPS / TLS 1.2+ (SNI: apim-ht-ss-p-cin-01)
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ Azure API Management (APIM) (Shared-services Sub: 859a785c | Region: CIN) │
 │ Hostname: apim-ht-ss-p-cin-01.azure-api.net (Consumption Tier)             │
 │ • Rate Limiting: 60 requests/min per client IP                            │
 │ • URL Rewrite: /bankc/api/v1/* ➔ /api/v1/*                                │
 │ • CORS Policy: Allowed Origin = https://bank.mytaxbot.site                │
 └─────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       │ 3. Forwarded HTTP (TCP 80)
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ Azure Kubernetes Service (AKS Spoke VNet: 10.42.0.0/16, Apps-prod Sub)    │
 │ Cluster: aks-ht-bankc-p-cin-01 | Node Pool: Standard_B4ms (Central India) │
 │                                                                           │
 │ ┌───────────────────────────────────────────────────────────────────────┐ │
 │ │ Azure Public LoadBalancer (Frontend IP: 20.x.x.x:80)                  │ │
 │ └───────────────────────────────────┬───────────────────────────────────┘ │
 │                                     │                                     │
 │                                     ▼                                     │
 │ ┌───────────────────────────────────────────────────────────────────────┐ │
 │ │ Namespace: bank-compliance (Azure CNI Overlay: 192.168.0.0/16)        │ │
 │ │                                                                       │ │
 │ │  [ Service: bankc-backend-svc ] (Type: LoadBalancer, Port: 80)        │ │
 │ │          │                                                            │ │
 │ │          │ 4. Forward to TargetPort 8000                              │ │
 │ │          ▼                                                            │ │
 │ │  [ Pod: bankc-backend (FastAPI) ] (IP: 192.168.1.14:8000)             │ │
 │ │          │                                                            │ │
 │ │          │ 5. In-Cluster Internal Vector Query (ClusterIP TCP 6333)   │ │
 │ │          ├────────────► [ Pod: qdrant-0 ] (IP: 192.168.1.18:6333)     │ │
 │ │          │              Storage: 4GB Azure Managed CSI (/qdrant/data) │ │
 │ │          │                                                            │ │
 │ │          │ 6. In-Cluster AI Proxy Request (ClusterIP TCP 4000)        │ │
 │ │          ├────────────► [ Pod: litellm-gateway ] (192.168.1.22:4000)  │ │
 │ │          │                     │                                      │ │
 │ │          │                     │ 7a. Primary: HTTPS 443               │ │
 │ │          │                     ├──────► Google Gemini 2.0 Flash       │ │
 │ │          │                     │                                      │ │
 │ │          │                     │ 7b. Standby Fallback: HTTPS 443      │ │
 │ │          │                     ├──────► Azure OpenAI (oai-ht-ss...)   │ │
 │ │          │                     │                                      │ │
 │ │          │                     │ 7c. Sovereign SLM: ClusterIP TCP 11434│
 │ │          │                     └──────► [ Pod: private-slm-inference] │
 │ │          │                              (IP: 192.168.1.25:11434)      │
 │ └──────────┴────────────────────────────────────────────────────────────┘ │
 └───────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive IP Addressing & CIDR Allocation Matrix

| VNet / Subnet Resource Name | Address Space (CIDR) | Usable IP Range | Purpose & Delegations | Gateway IP |
|:---|:---:|:---:|:---|:---:|
| **`vnet-ht-hub-p-cin-01` (Hub)** | `10.0.0.0/16` | `10.0.0.1 - 10.0.255.254` | Central Hub VNet in `Hub-prod` (3eb8cc01) | `10.0.0.1` |
| ├── `AzureFirewallSubnet` | `10.0.1.0/26` | `10.0.1.4 - 10.0.1.62` | Azure Firewall Premium / Standard | `10.0.1.1` |
| ├── `AzureBastionSubnet` | `10.0.2.0/26` | `10.0.2.4 - 10.0.2.62` | Azure Bastion Host for secure RDP/SSH | `10.0.2.1` |
| ├── `GatewaySubnet` | `10.0.3.0/27` | `10.0.3.4 - 10.0.3.30` | VPN / ExpressRoute Virtual Network Gateway | `10.0.3.1` |
| └── `snet-hub-mgmt` | `10.0.4.0/24` | `10.0.4.4 - 10.0.4.254` | Jumpbox and management agents | `10.0.4.1` |
| **`vnet-ht-taxb-p-cin-01` (TaxBot)** | `10.41.0.0/16` | `10.41.0.1 - 10.41.255.254` | Spoke 1 in `Apps-prod` (f4ffefe1) | `10.41.0.1` |
| ├── `snet-taxb-app` | `10.41.1.0/24` | `10.41.1.4 - 10.41.1.254` | Delegated to `Microsoft.Web/serverFarms` | `10.41.1.1` |
| └── `snet-taxb-pe` | `10.41.2.0/24` | `10.41.2.4 - 10.41.2.254` | Private Endpoints (Cosmos DB, AI Search) | `10.41.2.1` |
| **`vnet-ht-bankc-p-cin-01` (BankC)** | `10.42.0.0/16` | `10.42.0.1 - 10.42.255.254` | Spoke 2 in `Apps-prod` (f4ffefe1) | `10.42.0.1` |
| ├── `snet-bankc-aks-nodes` | `10.42.1.0/24` | `10.42.1.4 - 10.42.1.254` | AKS VM Node NICs (`aks-ht-bankc-p-cin-01`) | `10.42.1.1` |
| └── `snet-bankc-pe` | `10.42.2.0/24` | `10.42.2.4 - 10.42.2.254` | Private Endpoints (Key Vault, Storage) | `10.42.2.1` |
| **AKS Pod Network (Overlay)** | `192.168.0.0/16` | `192.168.0.1 - 192.168.255.254` | Azure CNI Overlay Pod Address Space | N/A (Overlay) |
| └── `bank-compliance` Pods | `192.168.1.0/24` | `192.168.1.1 - 192.168.1.254` | Dynamic Pod IPs assigned by Cilium/CNI | Pod-specific |
| **Kubernetes Service CIDR** | `10.240.0.0/16` | `10.240.0.1 - 10.240.255.254` | Internal `ClusterIP` virtual IPs | N/A (Kube-Proxy)|

---

## 4. Kubernetes In-Cluster Internal DNS Resolution Table

Inside the `bank-compliance` namespace, microservices communicate strictly using internal **CoreDNS Service FQDNs**. No public IPs are allocated to internal components:

| Microservice Component | Service Name | Service Type | Internal Cluster DNS Endpoint | Port / Protocol |
|:---|:---|:---:|:---|:---:|
| **FastAPI Backend Service** | `bankc-backend` | `LoadBalancer` | `bankc-backend.bank-compliance.svc.cluster.local` | `80:8000 TCP` |
| **LiteLLM Gateway Proxy** | `litellm` | `ClusterIP` | `litellm.bank-compliance.svc.cluster.local` | `4000 TCP` |
| **Qdrant Vector Database** | `qdrant` | `ClusterIP` | `qdrant.bank-compliance.svc.cluster.local` | `6333 (HTTP) / 6334 (gRPC)` |
| **In-Cluster Private SLM** | `private-slm-inference` | `ClusterIP` | `private-slm-inference.bank-compliance.svc.cluster.local` | `11434 TCP` |
| **Prometheus Server** | `monitoring-prometheus`| `ClusterIP` | `monitoring-prometheus.monitoring.svc.cluster.local` | `9090 TCP` |
| **Grafana Dashboard** | `monitoring-grafana` | `ClusterIP` | `monitoring-grafana.monitoring.svc.cluster.local` | `80 TCP` |

---

## 5. Low-Level Azure APIM Ingress Gateway Policy Configuration

The following XML inbound policy is applied to the `/bankc` API on `apim-ht-ss-p-cin-01` to enforce **rate-limiting, CORS, and URL rewrites**:

```xml
<policies>
    <inbound>
        <base />
        <!-- 1. Strict CORS Policy for bank.mytaxbot.site -->
        <cors allow-credentials="true">
            <allowed-origins>
                <origin>https://bank.mytaxbot.site</origin>
                <origin>https://www.bank.mytaxbot.site</origin>
                <origin>http://localhost:5173</origin>
            </allowed-origins>
            <allowed-methods>
                <method>GET</method>
                <method>POST</method>
                <method>OPTIONS</method>
            </allowed-methods>
            <allowed-headers>
                <header>*</header>
            </allowed-headers>
        </cors>

        <!-- 2. Rate Limiting: 60 requests per minute per Client IP -->
        <rate-limit-by-key calls="60" renewal-period="60" 
                           counter-key="@(context.Request.IpAddress)" 
                           increment-condition="@(context.Response.StatusCode >= 200 && context.Response.StatusCode < 400)" />

        <!-- 3. Strip /bankc prefix and forward to AKS LoadBalancer -->
        <rewrite-uri template="@(context.Request.Url.Path.Replace(&quot;/bankc&quot;, &quot;&quot;))" />
        <set-backend-service base-url="http://aks-ht-bankc-p-cin-01-lb.centralindia.cloudapp.azure.com" />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
        <!-- 4. Security Headers -->
        <set-header name="X-Content-Type-Options" exists-action="override">
            <value>nosniff</value>
        </set-header>
        <set-header name="X-Frame-Options" exists-action="override">
            <value>DENY</value>
        </set-header>
        <set-header name="Strict-Transport-Security" exists-action="override">
            <value>max-age=31536000; includeSubDomains; preload</value>
        </set-header>
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
```

---

## 6. Network Security Group (NSG) Rule Specification

### NSG: `nsg-ht-bankc-aks-p-cin-01` (Attached to `snet-bankc-aks-nodes`)

| Priority | Direction | Rule Name | Source IP / Tag | Source Port | Dest IP / Tag | Dest Port | Protocol | Action | Description |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **100** | Inbound | `AllowAPIMToAKS` | `ApiManagement` | `*` | `VirtualNetwork` | `80, 443` | `TCP` | **Allow** | Allows APIM gateway to invoke backend API |
| **110** | Inbound | `AllowAzureLoadBalancer` | `AzureLoadBalancer` | `*` | `VirtualNetwork` | `*` | `TCP` | **Allow** | Health probes from Azure Infrastructure |
| **200** | Inbound | `AllowVNetPeering` | `VirtualNetwork` | `*` | `VirtualNetwork` | `*` | `Any` | **Allow** | Inter-VNet communication via Hub peering |
| **4000** | Inbound | `DenyAllInbound` | `*` | `*` | `*` | `*` | `Any` | **Deny** | Default explicit deny for perimeter security |
| **100** | Outbound | `AllowOutboundToAzureOpenAI` | `VirtualNetwork` | `*` | `CognitiveServicesManagement` | `443` | `TCP` | **Allow** | Egress to Azure OpenAI Service in East US |
| **110** | Outbound | `AllowOutboundToGoogleAI` | `VirtualNetwork` | `*` | `Internet` | `443` | `TCP` | **Allow** | Egress to Google AI Studio Gemini Fleet |
| **120** | Outbound | `AllowOutboundToStorage` | `VirtualNetwork` | `*` | `Storage` | `443` | `TCP` | **Allow** | Access to Remote State & Raw PDFs Lake |
| **130** | Outbound | `AllowOutboundToKeyVault` | `VirtualNetwork` | `*` | `AzureKeyVault` | `443` | `TCP` | **Allow** | Workload Identity token & secret retrieval |

---

## 7. Zero-Egress Sovereign Banking Enforcement

To ensure compliance with **RBI Master Directions on Cyber Security & Data Localization**:
1. **Qdrant Vector Database:** Configured as `ClusterIP` on port `6333`. It has **zero public IP** and cannot be reached from outside the AKS virtual network.
2. **In-Cluster Sovereign SLM:** Hosted locally on CPU within the cluster (`private-slm-inference:11434`). Under sovereign mode, prompt tokens never leave the Kubernetes pod boundary.
3. **Data Localization:** All persistent disks (CSI Managed Disks) reside exclusively in **Azure Central India (Pune)**.
