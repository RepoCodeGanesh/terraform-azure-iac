import re
from typing import Tuple, List

# Indian Financial PII Regex Patterns
PAN_REGEX = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
AADHAAR_REGEX = re.compile(r'\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b')
BANK_ACC_REGEX = re.compile(r'\b[0-9]{9,18}\b')
PHONE_REGEX = re.compile(r'\b(?:\+91|91)?[6-9]\d{9}\b')

def redact_pii(text: str) -> Tuple[str, List[str]]:
    """
    Scans input prompt for Indian Banking PII and redacts it before sending to LLM.
    Returns (sanitized_text, list_of_redacted_types)
    """
    detected_pii = []
    
    if PAN_REGEX.search(text):
        detected_pii.append("PAN Card")
        text = PAN_REGEX.sub("[PAN-REDACTED]", text)
        
    if AADHAAR_REGEX.search(text):
        detected_pii.append("Aadhaar Number")
        text = AADHAAR_REGEX.sub("[AADHAAR-REDACTED]", text)
        
    if PHONE_REGEX.search(text):
        detected_pii.append("Mobile Number")
        text = PHONE_REGEX.sub("[PHONE-REDACTED]", text)
        
    return text, detected_pii
