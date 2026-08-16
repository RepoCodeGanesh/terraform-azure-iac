# Architecture & Request Lifecycle

```
  [ Branch Officer / React SPA ]
                â”‚
                â–¼ (HTTPS / DNS: bank.mytaxbot.site)
  [ Azure APIM Gateway ]  (IP Rate Limit: 20/min & CORS)
                â”‚
                â–¼ (AKS Ingress: 10.42.1.0/24)
  [ FastAPI Backend Pod ]
    â”œâ”€â”€ [ PII Redactor ] â”€â”€â–º Auto-masks PAN / Aadhaar / Account #s
    â”œâ”€â”€ [ Content Safety F0 ] â”€â”€â–º Prompt Injection & Jailbreak Shield
    â””â”€â”€ [ Qdrant Vector DB (4GB CSI Disk) ] â”€â”€â–º Retrieves RBI Master Direction Clauses
                â”‚
                â–¼
  [ LiteLLM Proxy Gateway Pod ]
    â”œâ”€â”€ Quota Check: Enforces user/department token budgets
    â”œâ”€â”€ KV Prompt Cache: Serves repeat questions in <20ms at $0
    â””â”€â”€ Cloud Forwarding: Routes to Azure OpenAI (gpt-5.4-nano)
                â”‚
                â–¼
  [ Instant Sub-Second Response with Exact Clause Citations ]
```