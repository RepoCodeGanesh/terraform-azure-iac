"""
Generate Clean, Minimalist Enterprise Visio Architectural Diagrams
===================================================================
Light background (#FFFFFF / #F8FAFC), crisp borders, standard Microsoft
enterprise architecture styling, high contrast text, and clear routing paths.
"""

from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. CLEAN VISIO NETWORK INGRESS & TRAFFIC FLOW (Page 09)
SVG_NETWORK_CLEAN = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" width="100%" height="100%" style="background:#ffffff; font-family:'Segoe UI', Arial, sans-serif;">
  <defs>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#0078d4"/>
    </marker>
    <marker id="arrow-gray" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#475569"/>
    </marker>
  </defs>

  <!-- Canvas Border -->
  <rect x="15" y="15" width="1170" height="650" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>

  <!-- Title & Header Bar -->
  <rect x="15" y="15" width="1170" height="50" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
  <text x="35" y="46" fill="#0f172a" font-size="16" font-weight="700">HappyTechies Cloud Platform — End-to-End Network Topology &amp; Ingress Specification</text>
  <text x="1050" y="46" fill="#64748b" font-size="12" font-weight="600">Doc: CR-NET-09</text>

  <!-- 1. Client Tier -->
  <g transform="translate(35, 90)">
    <rect width="180" height="540" rx="4" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
    <rect x="0" y="0" width="180" height="35" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"/>
    <text x="90" y="23" fill="#0f172a" font-size="13" font-weight="700" text-anchor="middle">Client Perimeter</text>

    <!-- Client Box -->
    <rect x="15" y="55" width="150" height="110" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="90" y="85" fill="#0078d4" font-size="13" font-weight="700" text-anchor="middle">Web Browser</text>
    <text x="90" y="105" fill="#334155" font-size="11" text-anchor="middle">bank.mytaxbot.site</text>
    <text x="90" y="125" fill="#64748b" font-size="10" text-anchor="middle">React 18 SPA</text>
    <text x="90" y="145" fill="#059669" font-size="10" font-weight="600" text-anchor="middle">DPDP PII Auto-Mask</text>

    <!-- Specs -->
    <rect x="15" y="185" width="150" height="330" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="210" fill="#0f172a" font-size="11" font-weight="700">CONNECTION SPECS:</text>
    <text x="25" y="235" fill="#334155" font-size="10">• Protocol: HTTPS</text>
    <text x="25" y="255" fill="#334155" font-size="10">• TLS: Version 1.3 / 1.2</text>
    <text x="25" y="275" fill="#334155" font-size="10">• Port: 443 (TCP)</text>
    <text x="25" y="305" fill="#0f172a" font-size="11" font-weight="700">SECURITY POSTURE:</text>
    <text x="25" y="330" fill="#334155" font-size="10">• Zero static secrets</text>
    <text x="25" y="350" fill="#334155" font-size="10">• Client-side masking</text>
    <text x="25" y="370" fill="#334155" font-size="10">• Ephemeral sessions</text>
  </g>

  <!-- Flow: Client -> Cloudflare -->
  <line x1="215" y1="150" x2="265" y2="150" stroke="#0078d4" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="240" y="140" fill="#0078d4" font-size="10" font-weight="700" text-anchor="middle">HTTPS:443</text>

  <!-- 2. Cloudflare Edge -->
  <g transform="translate(270, 90)">
    <rect width="200" height="540" rx="4" fill="#f8fafc" stroke="#f59e0b" stroke-width="1.5"/>
    <rect x="0" y="0" width="200" height="35" fill="#fef3c7" stroke="#f59e0b" stroke-width="1"/>
    <text x="100" y="23" fill="#92400e" font-size="13" font-weight="700" text-anchor="middle">Cloudflare Edge Network</text>

    <rect x="15" y="55" width="170" height="460" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="85" fill="#b45309" font-size="11" font-weight="700">EDGE SERVICES:</text>
    <text x="25" y="110" fill="#334155" font-size="10">• Anycast DNS CNAME</text>
    <text x="25" y="130" fill="#334155" font-size="10">• Layer 7 DDoS Mitigation</text>
    <text x="25" y="150" fill="#334155" font-size="10">• Full (Strict) SSL Offload</text>
    <text x="25" y="170" fill="#334155" font-size="10">• Static Asset Caching</text>
    
    <line x1="25" y1="195" x2="175" y2="195" stroke="#e2e8f0" stroke-width="1"/>
    <text x="25" y="220" fill="#b45309" font-size="11" font-weight="700">ORIGIN TARGETS:</text>
    <text x="25" y="245" fill="#334155" font-size="10">1. UI Static Web App:</text>
    <text x="25" y="262" fill="#0078d4" font-size="10">stapp-ht-bankc-p-cin-01</text>
    <text x="25" y="295" fill="#334155" font-size="10">2. API Gateway (APIM):</text>
    <text x="25" y="312" fill="#0078d4" font-size="10">apim-ht-ss-p-cin-01</text>
  </g>

  <!-- Flow: Cloudflare -> APIM -->
  <line x1="470" y1="300" x2="520" y2="300" stroke="#0078d4" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="495" y="290" fill="#0078d4" font-size="10" font-weight="700" text-anchor="middle">HTTPS:443</text>

  <!-- 3. Azure APIM Gateway (Shared Services) -->
  <g transform="translate(525, 90)">
    <rect width="210" height="540" rx="4" fill="#f8fafc" stroke="#0078d4" stroke-width="1.5"/>
    <rect x="0" y="0" width="210" height="35" fill="#e0f2fe" stroke="#0078d4" stroke-width="1"/>
    <text x="105" y="23" fill="#0369a1" font-size="13" font-weight="700" text-anchor="middle">Azure API Management</text>

    <rect x="15" y="55" width="180" height="460" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="85" fill="#0369a1" font-size="11" font-weight="700">GATEWAY POLICIES:</text>
    <text x="25" y="105" fill="#64748b" font-size="9">apim-ht-ss-p-cin-01 (Consumption)</text>
    
    <text x="25" y="135" fill="#0f172a" font-size="10" font-weight="700">1. CORS Whitelist:</text>
    <text x="25" y="152" fill="#334155" font-size="10">https://bank.mytaxbot.site</text>

    <text x="25" y="182" fill="#0f172a" font-size="10" font-weight="700">2. Rate Limiting:</text>
    <text x="25" y="199" fill="#334155" font-size="10">60 req/min per Client IP</text>

    <text x="25" y="229" fill="#0f172a" font-size="10" font-weight="700">3. URL Rewrite:</text>
    <text x="25" y="246" fill="#334155" font-size="10">/bankc/api/* ➔ /api/*</text>

    <text x="25" y="276" fill="#0f172a" font-size="10" font-weight="700">4. Backend Target:</text>
    <text x="25" y="293" fill="#334155" font-size="10">AKS Public LoadBalancer</text>
    <text x="25" y="310" fill="#64748b" font-size="9">Port: 80 (TCP Forward)</text>
  </g>

  <!-- Flow: APIM -> AKS Spoke -->
  <line x1="735" y1="300" x2="780" y2="300" stroke="#0078d4" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="758" y="290" fill="#0078d4" font-size="10" font-weight="700" text-anchor="middle">HTTP:80</text>

  <!-- 4. Azure Kubernetes Service (AKS Spoke VNet) -->
  <g transform="translate(785, 90)">
    <rect width="380" height="540" rx="4" fill="#f8fafc" stroke="#3b82f6" stroke-width="1.5"/>
    <rect x="0" y="0" width="380" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
    <text x="190" y="23" fill="#1d4ed8" font-size="13" font-weight="700" text-anchor="middle">AKS Spoke VNet (10.42.0.0/16) | Overlay: 192.168.0.0/16</text>

    <!-- FastAPI Backend Pod -->
    <rect x="15" y="55" width="350" height="115" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="80" fill="#1d4ed8" font-size="12" font-weight="700">FastAPI Backend (bankc-backend-svc:8000)</text>
    <text x="25" y="100" fill="#334155" font-size="10">• Pod IP: 192.168.1.14 (Azure CNI Overlay)</text>
    <text x="25" y="118" fill="#334155" font-size="10">• 4-Microagent State Machine (Supervisor, Retriever, Auditor, Synthesizer)</text>
    <text x="25" y="136" fill="#059669" font-size="10" font-weight="600">• Governed Semantic Vector Cache (&lt;10ms, Cosine &gt;= 0.90, $0.00)</text>
    <text x="25" y="154" fill="#334155" font-size="10">• OpenTelemetry GenAI Semantic Spans (v1.26+ Standard)</text>

    <!-- Zero Egress Box -->
    <rect x="15" y="185" width="350" height="330" rx="4" fill="#f1f5f9" stroke="#10b981" stroke-width="1.5"/>
    <text x="25" y="210" fill="#047857" font-size="11" font-weight="700">INTERNAL CLUSTERIP TIER (ZERO PUBLIC EGRESS)</text>

    <!-- Qdrant -->
    <rect x="25" y="225" width="330" height="75" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="35" y="248" fill="#b91c1c" font-size="11" font-weight="700">Qdrant Vector Database (qdrant:6333)</text>
    <text x="35" y="268" fill="#334155" font-size="10">• 4GB Azure Managed Disk (E1 SSD, ~$0.15/mo) mounted at /qdrant/data</text>
    <text x="35" y="286" fill="#334155" font-size="10">• HNSW Dense Vector Indexing | ClusterIP: 10.240.12.80</text>

    <!-- LiteLLM Gateway -->
    <rect x="25" y="310" width="330" height="95" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="35" y="333" fill="#047857" font-size="11" font-weight="700">LiteLLM AI Proxy Gateway (litellm:4000)</text>
    <text x="35" y="353" fill="#334155" font-size="10">• 1. Primary Route: Google Gemini 2.0 Flash (HTTPS:443)</text>
    <text x="35" y="371" fill="#334155" font-size="10">• 2. Standby Route: Azure OpenAI gpt-5.4-nano (East US)</text>
    <text x="35" y="389" fill="#334155" font-size="10">• 3. Sovereign Route: In-Cluster Private SLM (Local CPU)</text>

    <!-- Private SLM -->
    <rect x="25" y="415" width="330" height="85" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="35" y="438" fill="#6d28d9" font-size="11" font-weight="700">Private Sovereign SLM (private-slm:11434)</text>
    <text x="35" y="458" fill="#334155" font-size="10">• CPU Qwen-2.5 / Phi-3 (Ollama Engine, &lt;1GB RAM)</text>
    <text x="35" y="476" fill="#334155" font-size="10">• Zero External Token Egress (100% On-Cluster Privacy)</text>
  </g>
</svg>'''

# 2. CLEAN VISIO 4-SUBSCRIPTION CAF LANDING ZONE (Page 01)
SVG_CAF_CLEAN = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" width="100%" height="100%" style="background:#ffffff; font-family:'Segoe UI', Arial, sans-serif;">
  <!-- Canvas Border -->
  <rect x="15" y="15" width="1170" height="650" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>

  <!-- Title Bar -->
  <rect x="15" y="15" width="1170" height="50" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
  <text x="35" y="46" fill="#0f172a" font-size="16" font-weight="700">HappyTechies Cloud Platform — 4-Subscription CAF Landing Zone &amp; State Map</text>
  <text x="1050" y="46" fill="#64748b" font-size="12" font-weight="600">Doc: CR-CAF-01</text>

  <!-- Tenant Box -->
  <rect x="35" y="80" width="1130" height="55" rx="4" fill="#f8fafc" stroke="#0078d4" stroke-width="1.5"/>
  <text x="600" y="105" fill="#0078d4" font-size="13" font-weight="700" text-anchor="middle">Microsoft Entra ID Tenant: 4cef0d84-84d6-4ed0-8abe-773b015bcf99 (MyTaxBot)</text>
  <text x="600" y="123" fill="#475569" font-size="11" text-anchor="middle">Zero-Trust Workload Identity Federation (OIDC) | Dual CI/CD: GitHub Actions &amp; Azure DevOps</text>

  <!-- 4 Subscriptions Grid -->
  <!-- Sub 1: Bootstrap -->
  <g transform="translate(35, 150)">
    <rect width="265" height="490" rx="4" fill="#f8fafc" stroke="#64748b" stroke-width="1.5"/>
    <rect x="0" y="0" width="265" height="35" fill="#e2e8f0" stroke="#64748b" stroke-width="1"/>
    <text x="132" y="23" fill="#0f172a" font-size="13" font-weight="700" text-anchor="middle">1. Bootstrap Sub</text>

    <rect x="15" y="50" width="235" height="420" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="75" fill="#334155" font-size="10" font-weight="700">ID: 7689ad81-71ba-481b-a17c</text>
    
    <text x="25" y="105" fill="#0f172a" font-size="11" font-weight="700">CENTRAL STATE BACKEND:</text>
    <text x="25" y="128" fill="#334155" font-size="10">• Storage: sthtbootpcin01</text>
    <text x="25" y="146" fill="#334155" font-size="10">• Container: tfstate</text>
    <text x="25" y="164" fill="#334155" font-size="10">• Auth: use_azuread_auth</text>
    <text x="25" y="182" fill="#334155" font-size="10">• Key Vault: kv-ht-boot-p-cin-01</text>

    <line x1="25" y1="205" x2="225" y2="205" stroke="#e2e8f0" stroke-width="1"/>
    <text x="25" y="230" fill="#0f172a" font-size="11" font-weight="700">STATE KEYS ISOLATED:</text>
    <text x="25" y="255" fill="#334155" font-size="10">1. bootstrap/prod.tfstate</text>
    <text x="25" y="275" fill="#334155" font-size="10">2. hub/prod.tfstate</text>
    <text x="25" y="295" fill="#334155" font-size="10">3. shared-services/prod.tfstate</text>
    <text x="25" y="315" fill="#334155" font-size="10">4. workloads/tax-advisor/prod</text>
    <text x="25" y="335" fill="#334155" font-size="10">5. workloads/bank-compliance</text>
  </g>

  <!-- Sub 2: Hub-prod -->
  <g transform="translate(320, 150)">
    <rect width="265" height="490" rx="4" fill="#f8fafc" stroke="#d97706" stroke-width="1.5"/>
    <rect x="0" y="0" width="265" height="35" fill="#fef3c7" stroke="#d97706" stroke-width="1"/>
    <text x="132" y="23" fill="#92400e" font-size="13" font-weight="700" text-anchor="middle">2. Hub-prod Sub</text>

    <rect x="15" y="50" width="235" height="420" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="75" fill="#334155" font-size="10" font-weight="700">ID: 3eb8cc01-50c6-473e-8d5f</text>

    <text x="25" y="105" fill="#b45309" font-size="11" font-weight="700">PERIMETER NETWORK:</text>
    <text x="25" y="128" fill="#334155" font-size="10">• Hub VNet (10.0.0.0/16)</text>
    <text x="25" y="146" fill="#334155" font-size="10">• AzureFirewallSubnet (10.0.1.0/26)</text>
    <text x="25" y="164" fill="#334155" font-size="10">• AzureBastionSubnet (10.0.2.0/26)</text>
    <text x="25" y="182" fill="#334155" font-size="10">• GatewaySubnet (10.0.3.0/27)</text>

    <line x1="25" y1="205" x2="225" y2="205" stroke="#e2e8f0" stroke-width="1"/>
    <text x="25" y="230" fill="#b45309" font-size="11" font-weight="700">HUB-SPOKE PEERING:</text>
    <text x="25" y="255" fill="#334155" font-size="10">↔ TaxBot Spoke (10.41.0.0/16)</text>
    <text x="25" y="275" fill="#334155" font-size="10">↔ BankCompliance (10.42.0.0/16)</text>
    <text x="25" y="295" fill="#334155" font-size="10">↔ Shared Services (10.43.0.0/16)</text>
  </g>

  <!-- Sub 3: Shared-services -->
  <g transform="translate(605, 150)">
    <rect width="265" height="490" rx="4" fill="#f8fafc" stroke="#0078d4" stroke-width="1.5"/>
    <rect x="0" y="0" width="265" height="35" fill="#e0f2fe" stroke="#0078d4" stroke-width="1"/>
    <text x="132" y="23" fill="#0369a1" font-size="13" font-weight="700" text-anchor="middle">3. Shared-services Sub</text>

    <rect x="15" y="50" width="235" height="420" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="75" fill="#334155" font-size="10" font-weight="700">ID: 859a785c-bd38-402d-b595</text>

    <text x="25" y="105" fill="#0369a1" font-size="11" font-weight="700">SHARED PLATFORM:</text>
    <text x="25" y="128" fill="#334155" font-size="10">• Azure APIM (apim-ht-ss)</text>
    <text x="25" y="146" fill="#334155" font-size="10">• Log Analytics (law-ht-ss)</text>
    <text x="25" y="164" fill="#334155" font-size="10">• Shared Key Vault (kv-ht-ss)</text>
    <text x="25" y="182" fill="#334155" font-size="10">• AI Content Safety F0</text>

    <line x1="25" y1="205" x2="225" y2="205" stroke="#e2e8f0" stroke-width="1"/>
    <text x="25" y="230" fill="#0369a1" font-size="11" font-weight="700">SECRETS HOSTED:</text>
    <text x="25" y="255" fill="#334155" font-size="10">✓ confluence-api-token</text>
    <text x="25" y="275" fill="#334155" font-size="10">✓ azure-openai-key</text>
  </g>

  <!-- Sub 4: Apps-prod -->
  <g transform="translate(890, 150)">
    <rect width="275" height="490" rx="4" fill="#f8fafc" stroke="#16a34a" stroke-width="1.5"/>
    <rect x="0" y="0" width="275" height="35" fill="#dcfce7" stroke="#16a34a" stroke-width="1"/>
    <text x="137" y="23" fill="#15803d" font-size="13" font-weight="700" text-anchor="middle">4. Apps-prod Sub</text>

    <rect x="15" y="50" width="245" height="420" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="75" fill="#334155" font-size="10" font-weight="700">ID: f4ffefe1-d689-4059-969c</text>

    <text x="25" y="105" fill="#15803d" font-size="11" font-weight="700">WORKLOAD 1: TAXBOT</text>
    <text x="25" y="128" fill="#334155" font-size="10">• Python Function App Y1</text>
    <text x="25" y="146" fill="#334155" font-size="10">• Azure AI Search + Cosmos DB</text>
    <text x="25" y="164" fill="#0078d4" font-size="10">  www.mytaxbot.site</text>

    <line x1="25" y1="185" x2="235" y2="185" stroke="#e2e8f0" stroke-width="1"/>
    <text x="25" y="210" fill="#15803d" font-size="11" font-weight="700">WORKLOAD 2: BANKCOMPLIANCE</text>
    <text x="25" y="233" fill="#334155" font-size="10">• AKS Free Tier (Standard_B4ms)</text>
    <text x="25" y="251" fill="#334155" font-size="10">• Qdrant Vector DB (4GB CSI)</text>
    <text x="25" y="269" fill="#334155" font-size="10">• LiteLLM Multi-Cloud Gateway</text>
    <text x="25" y="287" fill="#334155" font-size="10">• In-Cluster Sovereign SLM</text>
    <text x="25" y="305" fill="#0078d4" font-size="10">  bank.mytaxbot.site</text>
  </g>
</svg>'''

# 3. CLEAN VISIO BANKCOMPLIANCE AI ARCHITECTURE (Page 03)
SVG_BANKC_CLEAN = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" width="100%" height="100%" style="background:#ffffff; font-family:'Segoe UI', Arial, sans-serif;">
  <rect x="15" y="15" width="1170" height="650" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>

  <!-- Title Bar -->
  <rect x="15" y="15" width="1170" height="50" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
  <text x="35" y="46" fill="#0f172a" font-size="16" font-weight="700">Workload 2: BankCompliance AI — 4-Microagent AKS &amp; Inference Architecture</text>
  <text x="1050" y="46" fill="#64748b" font-size="12" font-weight="600">Doc: CR-APP-03</text>

  <!-- Left: Ingress Tier -->
  <g transform="translate(35, 80)">
    <rect width="250" height="560" rx="4" fill="#f8fafc" stroke="#0284c7" stroke-width="1.5"/>
    <rect x="0" y="0" width="250" height="35" fill="#e0f2fe" stroke="#0284c7" stroke-width="1"/>
    <text x="125" y="23" fill="#0369a1" font-size="13" font-weight="700" text-anchor="middle">1. Client &amp; Edge Ingress</text>

    <!-- Web App -->
    <rect x="15" y="50" width="220" height="120" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="75" fill="#0284c7" font-size="11" font-weight="700">REACT SPA (AZURE SWA):</text>
    <text x="25" y="98" fill="#334155" font-size="10">• Split-Screen Regulatory Viewer</text>
    <text x="25" y="116" fill="#334155" font-size="10">• Deep-Linked RBI Citations</text>
    <text x="25" y="134" fill="#334155" font-size="10">• Native GenAIOps Telemetry</text>
    <text x="25" y="155" fill="#0078d4" font-size="10">https://bank.mytaxbot.site</text>

    <!-- APIM -->
    <rect x="15" y="185" width="220" height="140" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="210" fill="#0369a1" font-size="11" font-weight="700">AZURE APIM GATEWAY:</text>
    <text x="25" y="233" fill="#334155" font-size="10">• Rate Limit: 60 calls/min/IP</text>
    <text x="25" y="251" fill="#334155" font-size="10">• CORS: bank.mytaxbot.site</text>
    <text x="25" y="269" fill="#334155" font-size="10">• URL Rewrite: /bankc/api/* ➔ /api/*</text>
    <text x="25" y="287" fill="#059669" font-size="10" font-weight="600">✓ Consumption ($0.00 Idle)</text>

    <!-- DPDP PII -->
    <rect x="15" y="340" width="220" height="185" rx="4" fill="#ffffff" stroke="#16a34a" stroke-width="1"/>
    <text x="25" y="365" fill="#15803d" font-size="11" font-weight="700">DPDP ACT PII SANITIZER:</text>
    <text x="25" y="388" fill="#334155" font-size="10">• Real-time Regex + NER Masking</text>
    <text x="25" y="410" fill="#b91c1c" font-size="10">❌ [PAN-REDACTED]</text>
    <text x="25" y="428" fill="#b91c1c" font-size="10">❌ [AADHAAR-REDACTED]</text>
    <text x="25" y="446" fill="#b91c1c" font-size="10">❌ [CARD-REDACTED]</text>
    <text x="25" y="475" fill="#059669" font-size="10" font-weight="600">Zero PII Egress Guarantee</text>
  </g>

  <!-- Center: 4-Agent Orchestrator -->
  <g transform="translate(305, 80)">
    <rect width="540" height="560" rx="4" fill="#f8fafc" stroke="#3b82f6" stroke-width="1.5"/>
    <rect x="0" y="0" width="540" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
    <text x="270" y="23" fill="#1d4ed8" font-size="13" font-weight="700" text-anchor="middle">2. 4-Microagent State Graph Orchestrator (FastAPI Pod)</text>

    <!-- Cache -->
    <rect x="15" y="50" width="510" height="55" rx="4" fill="#ffffff" stroke="#10b981" stroke-width="1"/>
    <text x="25" y="73" fill="#047857" font-size="11" font-weight="700">⚡ Sub-10ms Governed Semantic Vector Cache</text>
    <text x="25" y="93" fill="#334155" font-size="10">Cosine Match (&gt;= 0.90) | Hit Rate: 94.2% | Latency: 8.4ms | Zero Token Cost</text>

    <!-- Agent 1 & 2 -->
    <rect x="15" y="115" width="245" height="105" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="138" fill="#0284c7" font-size="11" font-weight="700">🎯 SupervisorAgent</text>
    <text x="25" y="160" fill="#334155" font-size="10">• Domain Out-of-Scope Interceptor</text>
    <text x="25" y="178" fill="#334155" font-size="10">• &lt;10ms Non-Banking Rejection</text>
    <text x="25" y="196" fill="#64748b" font-size="9">Prevents Semantic Drift</text>

    <rect x="280" y="115" width="245" height="105" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="290" y="138" fill="#d97706" font-size="11" font-weight="700">🔍 RetrieverAgent</text>
    <text x="290" y="160" fill="#334155" font-size="10">• Tool Caller on Qdrant DB</text>
    <text x="290" y="178" fill="#334155" font-size="10">• Dense HNSW Top-5 Vector Search</text>
    <text x="290" y="196" fill="#64748b" font-size="9">Distance Threshold: 0.72</text>

    <!-- Agent 3 & 4 -->
    <rect x="15" y="230" width="245" height="115" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="253" fill="#db2777" font-size="11" font-weight="700">🧠 AuditorAgent (Reflection)</text>
    <text x="25" y="275" fill="#334155" font-size="10">• Groundedness &amp; Relevance Critic</text>
    <text x="25" y="293" fill="#334155" font-size="10">• Max Iterations: 2 (Prevents loops)</text>
    <text x="25" y="311" fill="#64748b" font-size="9">Injects query refinements on missing facts</text>

    <rect x="280" y="230" width="245" height="115" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="290" y="253" fill="#059669" font-size="11" font-weight="700">✍️ SynthesizerAgent</text>
    <text x="290" y="275" fill="#334155" font-size="10">• Formats RBI Statutory Citations</text>
    <text x="290" y="293" fill="#334155" font-size="10">• Deep-Link Clause Inspection URLs</text>
    <text x="290" y="311" fill="#64748b" font-size="9">Groundedness Score: 4.68/5.0</text>

    <!-- OpenTelemetry -->
    <rect x="15" y="355" width="510" height="170" rx="4" fill="#ffffff" stroke="#6366f1" stroke-width="1"/>
    <text x="25" y="380" fill="#4338ca" font-size="11" font-weight="700">📊 OpenTelemetry GenAI Semantic Spans (v1.26+ Standard):</text>
    <text x="25" y="405" fill="#334155" font-size="10">• gen_ai.system = 'happytechies.bankc' | gen_ai.agent.name = ['Supervisor', 'Retriever', 'Auditor']</text>
    <text x="25" y="425" fill="#334155" font-size="10">• gen_ai.usage.input_tokens | gen_ai.usage.output_tokens | cache_hit = true/false</text>
    <text x="25" y="445" fill="#334155" font-size="10">• Prometheus /metrics endpoint on :8000</text>
    <text x="25" y="475" fill="#059669" font-size="10" font-weight="600">✓ Full distributed trace propagation across all 4 micro-agents</text>
  </g>

  <!-- Right: Storage & Inference -->
  <g transform="translate(865, 80)">
    <rect width="300" height="560" rx="4" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
    <rect x="0" y="0" width="300" height="35" fill="#e2e8f0" stroke="#475569" stroke-width="1"/>
    <text x="150" y="23" fill="#0f172a" font-size="13" font-weight="700" text-anchor="middle">3. Storage &amp; Inference Tier</text>

    <!-- Qdrant -->
    <rect x="15" y="50" width="270" height="135" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="75" fill="#b91c1c" font-size="11" font-weight="700">QDRANT VECTOR DB (CSI):</text>
    <text x="25" y="98" fill="#334155" font-size="10">• 4GB Azure Managed Disk (E1 SSD)</text>
    <text x="25" y="116" fill="#334155" font-size="10">• Persists across az aks stop/start</text>
    <text x="25" y="134" fill="#334155" font-size="10">• Cost: ~$0.15/month (₹12/mo)</text>
    <text x="25" y="156" fill="#0078d4" font-size="10">ClusterIP: qdrant:6333</text>

    <!-- LiteLLM -->
    <rect x="15" y="195" width="270" height="160" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="220" fill="#047857" font-size="11" font-weight="700">LITELLM AI PROXY GATEWAY:</text>
    <text x="25" y="243" fill="#334155" font-size="10">1. Primary: Google Gemini 2.0 Flash</text>
    <text x="25" y="261" fill="#334155" font-size="10">2. Fallback: Azure OpenAI gpt-5.4-nano</text>
    <text x="25" y="279" fill="#334155" font-size="10">3. Sovereign: In-Cluster Private SLM</text>
    <text x="25" y="303" fill="#64748b" font-size="9">Circuit Breaking on HTTP 429/500</text>
    <text x="25" y="325" fill="#0078d4" font-size="10">ClusterIP: litellm:4000</text>

    <!-- Sovereign SLM -->
    <rect x="15" y="365" width="270" height="160" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="25" y="390" fill="#6d28d9" font-size="11" font-weight="700">IN-CLUSTER SOVEREIGN SLM:</text>
    <text x="25" y="413" fill="#334155" font-size="10">• CPU Qwen-2.5 / Phi-3 (Ollama)</text>
    <text x="25" y="431" fill="#334155" font-size="10">• Memory: &lt;1GB RAM on AKS Node</text>
    <text x="25" y="449" fill="#334155" font-size="10">• Zero External Token Egress</text>
    <text x="25" y="473" fill="#059669" font-size="10" font-weight="600">100% Data Localization Compliance</text>
    <text x="25" y="495" fill="#0078d4" font-size="10">ClusterIP: private-slm:11434</text>
  </g>
</svg>'''

# Write clean SVG files
(OUTPUT_DIR / "09-enterprise-network-traffic-flow.svg").write_text(SVG_NETWORK_CLEAN, encoding="utf-8")
(OUTPUT_DIR / "01-caf-landing-zone-topology.svg").write_text(SVG_CAF_CLEAN, encoding="utf-8")
(OUTPUT_DIR / "03-bank-compliance-aks-architecture.svg").write_text(SVG_BANKC_CLEAN, encoding="utf-8")

print(f"Generated clean, plain Visio-style SVG architectural diagrams in: {OUTPUT_DIR}")
