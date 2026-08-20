import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "BankCompliance AI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # AI Gateway / LiteLLM Proxy
    LITELLM_URL: str = os.getenv("LITELLM_URL", "http://litellm:4000/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gemini-2.0-flash")
    
    # Qdrant Vector DB
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "rbi_master_directions")
    
    # Azure Content Safety
    CONTENT_SAFETY_ENDPOINT: str = os.getenv("CONTENT_SAFETY_ENDPOINT", "")
    
    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    class Config:
        case_sensitive = True

settings = Settings()

