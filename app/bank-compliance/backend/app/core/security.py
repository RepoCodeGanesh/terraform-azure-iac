import os
import logging
from azure.identity import DefaultAzureCredential
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions
    HAS_CONTENT_SAFETY = True
except ImportError:
    HAS_CONTENT_SAFETY = False

def get_content_safety_client():
    if not HAS_CONTENT_SAFETY or not settings.CONTENT_SAFETY_ENDPOINT:
        return None
    try:
        credential = DefaultAzureCredential()
        return ContentSafetyClient(settings.CONTENT_SAFETY_ENDPOINT, credential)
    except Exception as e:
        logger.warning(f"Content Safety client creation failed: {e}")
        return None
