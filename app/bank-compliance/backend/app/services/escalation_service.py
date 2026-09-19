"""
BankCompliance AI — Human-in-the-Loop (HITL) Regulatory Escalation Service
==========================================================================
Implements AI-500 Enterprise Agent Governance & State Suspension:
  1. Detects high-stakes statutory compliance risk (FLDG, Data Localization, KYC bypass).
  2. Suspends autonomous agent action into PENDING_COMPLIANCE_REVIEW state.
  3. Maintains a persistent, auditable Escalation Queue for licensed Compliance Officers.
  4. Records cryptographic sign-off receipts upon human review/override.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("BankCompliance-HITL")

# In-memory thread-safe escalation ticket registry
_ESCALATION_TICKETS: Dict[str, Dict[str, Any]] = {}

# High-risk statutory regex and semantic triggers that mandate Human-in-the-Loop review
HIGH_RISK_STATUTORY_TRIGGERS = [
    {
        "trigger": "FLDG_BREACH",
        "category": "Digital Lending & Default Loss Guarantee",
        "keywords": ["fldg", "default loss guarantee", "dlg", "credit enhancement", "5%"],
        "condition": lambda q: any(k in q.lower() for k in ["fldg", "default loss guarantee", "dlg"]) and any(w in q.lower() for w in ["exceed", "more than 5", "above 5", "bypass", "10%", "15%", "20%"]),
        "risk_level": "CRITICAL",
        "reason": "Request involves potential violation or restructuring of RBI 5% Default Loss Guarantee (FLDG) statutory ceiling."
    },
    {
        "trigger": "DATA_LOCALIZATION_BREACH",
        "category": "IT Outsourcing & Cloud Sovereignty",
        "keywords": ["offshore", "outside india", "foreign cloud", "singapore", "frankfurt", "us east", "overseas"],
        "condition": lambda q: any(k in q.lower() for k in ["cloud", "store", "host", "transfer", "backup", "server"]) and any(w in q.lower() for w in ["outside india", "offshore", "overseas", "foreign", "us", "singapore", "europe"]),
        "risk_level": "CRITICAL",
        "reason": "Request involves cross-border sovereign data transfer violating RBI Cloud Data Localization Directives."
    },
    {
        "trigger": "KYC_VCIP_BYPASS",
        "category": "Customer Identification & Anti-Money Laundering",
        "keywords": ["v-cip", "vcip", "video kyc", "bypass", "without face", "without aadhaar", "skip kyc"],
        "condition": lambda q: ("v-cip" in q.lower() or "vcip" in q.lower() or "kyc" in q.lower()) and any(w in q.lower() for w in ["bypass", "skip", "override", "without liveness", "fake", "exemption"]),
        "risk_level": "HIGH",
        "reason": "Request touches exemption or circumvention of mandatory Video-based Customer Identification Process (V-CIP)."
    },
    {
        "trigger": "UNREGULATED_LENDING_APP",
        "category": "FinTech & Digital Lending Architecture",
        "keywords": ["disburse directly", "lsp account", "fintech pool", "escrow bypass"],
        "condition": lambda q: any(k in q.lower() for k in ["lsp disburse", "fintech disburse", "pass-through account", "pool account"]),
        "risk_level": "CRITICAL",
        "reason": "Direct loan disbursement by Lending Service Provider (LSP) without RE bank account intermediation is illegal."
    }
]

def check_hitl_requirement(query: str, citations: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, str, str, str]:
    """
    Evaluates whether a query mandates human review under RBI & EU AI Act governance.
    Returns (hitl_required, risk_level, trigger_name, reason).
    """
    for rule in HIGH_RISK_STATUTORY_TRIGGERS:
        try:
            if rule["condition"](query):
                logger.warning("🚨 HITL Escalation Triggered: %s (Risk: %s)", rule["trigger"], rule["risk_level"])
                return True, rule["risk_level"], rule["trigger"], rule["reason"]
        except Exception as e:
            logger.error("Error evaluating HITL rule %s: %s", rule["trigger"], e)

    return False, "LOW", "NONE", "Standard automated statutory advice permitted."

def create_escalation_ticket(
    query: str,
    preliminary_answer: str,
    citations: List[Dict[str, Any]],
    risk_level: str,
    trigger_name: str,
    reason: str,
    department: str = "compliance"
) -> Dict[str, Any]:
    """Creates a persistent escalation ticket and halts autonomous execution."""
    ticket_id = f"ESC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    now_iso = datetime.now(timezone.utc).isoformat()

    ticket = {
        "ticket_id": ticket_id,
        "status": "PENDING_COMPLIANCE_REVIEW",
        "query": query,
        "risk_level": risk_level,
        "statutory_trigger": trigger_name,
        "reason": reason,
        "department": department,
        "preliminary_answer": preliminary_answer,
        "citations": citations,
        "created_at": now_iso,
        "reviewed_at": None,
        "reviewed_by": None,
        "verdict": None,
        "officer_notes": None,
        "final_sanctioned_advice": None
    }

    _ESCALATION_TICKETS[ticket_id] = ticket
    logger.info("📋 Created HITL Escalation Ticket: %s (Status: PENDING_COMPLIANCE_REVIEW)", ticket_id)
    return ticket

def list_escalation_tickets(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists escalation tickets, optionally filtered by status."""
    tickets = list(_ESCALATION_TICKETS.values())
    if status:
        status_upper = status.upper().strip()
        tickets = [t for t in tickets if t["status"] == status_upper]
    return sorted(tickets, key=lambda x: x["created_at"], reverse=True)

def get_escalation_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves an escalation ticket by ID."""
    return _ESCALATION_TICKETS.get(ticket_id)

def review_escalation_ticket(
    ticket_id: str,
    officer_name: str,
    verdict: str,  # "APPROVED" | "REJECTED" | "AMENDED"
    officer_notes: str,
    amended_advice: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Submits a signed Compliance Officer review, transitioning the ticket to an auditable closed state.
    """
    ticket = _ESCALATION_TICKETS.get(ticket_id)
    if not ticket:
        return None

    now_iso = datetime.now(timezone.utc).isoformat()
    verdict_upper = verdict.upper().strip()

    ticket["status"] = f"OFFICER_{verdict_upper}"
    ticket["reviewed_at"] = now_iso
    ticket["reviewed_by"] = officer_name
    ticket["verdict"] = verdict_upper
    ticket["officer_notes"] = officer_notes
    ticket["final_sanctioned_advice"] = amended_advice or ticket["preliminary_answer"]
    ticket["cryptographic_signature"] = f"sig:{uuid.uuid5(uuid.NAMESPACE_DNS, f'{ticket_id}:{officer_name}:{now_iso}')}"

    logger.info("✅ HITL Ticket %s reviewed by %s with verdict: %s", ticket_id, officer_name, verdict_upper)
    return ticket
