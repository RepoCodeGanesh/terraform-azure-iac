import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.routes import router as api_router
from app.core.config import settings

# Configure Azure Monitor OpenTelemetry if connection string is present
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_azure_monitor()
except Exception as e:
    logging.getLogger(__name__).debug("OpenTelemetry init skipped: %s", e)

app = FastAPI(
    title="BankCompliance AI API",
    description="Cloud-Native Banking Regulatory & Compliance Copilot API",
    version="1.0.0"
)

# Initialize Prometheus instrumentation for live observability & Grafana
Instrumentator().instrument(app).expose(app)

# Parse allowed origins
raw_origins = settings.ALLOWED_ORIGINS
if raw_origins == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/healthz", tags=["Health"])
async def healthz():
    return {"status": "healthy", "service": "bank-compliance-backend", "version": "1.0.0"}
