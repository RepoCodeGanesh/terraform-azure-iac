"""
Model Context Protocol (MCP) Agent Tool Bridge
Implements official Anthropic/Microsoft Model Context Protocol JSON-RPC specification (v2024-11-05).
Federates deterministic statutory calculation and verification tools for autonomous multi-agent systems.
"""

from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

# MCP Protocol Version
MCP_PROTOCOL_VERSION = "2024-11-05"

# Tool Schemas registered in MCP Server
MCP_TOOLS_MANIFEST: List[Dict[str, Any]] = [
    {
        "name": "calculate_fldg_cap",
        "description": "Calculates Default Loss Guarantee (FLDG) compliance against the RBI 5% regulatory ceiling (RBI/2023-24/53 Clause 6).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "total_portfolio_inr": {
                    "type": "number",
                    "description": "Total outstanding loan portfolio covered under the guarantee arrangement in INR."
                },
                "guarantee_amount_inr": {
                    "type": "number",
                    "description": "Total default loss guarantee provided by the Lending Service Provider (LSP) in INR."
                }
            },
            "required": ["total_portfolio_inr", "guarantee_amount_inr"]
        }
    },
    {
        "name": "check_data_localization",
        "description": "Evaluates cross-border data storage and processing compliance against the RBI 2018 Payment System Data localization directive (DPSS.CO.OD.No.2785/06.08.005/2017-18).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data_category": {
                    "type": "string",
                    "enum": ["card_payment_data", "upi_transaction_logs", "core_banking_balance", "customer_kyc_pii"],
                    "description": "Category of banking and payment data."
                },
                "storage_region": {
                    "type": "string",
                    "description": "Country or cloud region where end-to-end data resides at rest."
                },
                "is_cross_border_transaction": {
                    "type": "boolean",
                    "description": "Whether the transaction is international/cross-border."
                }
            },
            "required": ["data_category", "storage_region"]
        }
    },
    {
        "name": "verify_vcip_identity_step",
        "description": "Validates Video-based Customer Identification Process (V-CIP) mandatory statutory requirements under RBI KYC Master Directions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "live_geotag_in_india": {
                    "type": "boolean",
                    "description": "True if customer geolocation confirms presence within Indian territory."
                },
                "facial_liveness_verified": {
                    "type": "boolean",
                    "description": "True if automated liveliness match against official Aadhaar/PAN photo succeeded."
                },
                "aadhaar_xml_or_digilocker": {
                    "type": "boolean",
                    "description": "True if Offline Aadhaar XML or DigiLocker official verification was executed."
                }
            },
            "required": ["live_geotag_in_india", "facial_liveness_verified", "aadhaar_xml_or_digilocker"]
        }
    }
]


class MCPToolBridge:
    """
    In-process Model Context Protocol server and bridge.
    Provides standard JSON-RPC tool endpoints and direct agent execution bindings.
    """

    def __init__(self):
        self.tools = {
            "calculate_fldg_cap": self._execute_calculate_fldg_cap,
            "check_data_localization": self._execute_check_data_localization,
            "verify_vcip_identity_step": self._execute_verify_vcip_identity_step
        }

    def list_tools(self) -> Dict[str, Any]:
        """Returns the MCP tools manifest."""
        return {
            "protocol_version": MCP_PROTOCOL_VERSION,
            "tools": MCP_TOOLS_MANIFEST
        }

    def handle_jsonrpc(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processes an incoming standard JSON-RPC 2.0 MCP request."""
        req_id = request_payload.get("id", 1)
        method = request_payload.get("method")
        params = request_payload.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": self.list_tools()
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            try:
                content = self.call_tool(tool_name, args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(content)
                            }
                        ],
                        "isError": not content.get("compliant", False) if "compliant" in content else False
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found."
                }
            }

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Direct programmatic invocation of registered MCP tool."""
        handler = self.tools.get(tool_name)
        if not handler:
            raise ValueError(f"MCP Tool '{tool_name}' is not registered.")
        return handler(arguments)

    def _execute_calculate_fldg_cap(self, args: Dict[str, Any]) -> Dict[str, Any]:
        portfolio = float(args.get("total_portfolio_inr", 0.0))
        guarantee = float(args.get("guarantee_amount_inr", 0.0))

        if portfolio <= 0:
            return {
                "compliant": False,
                "error": "Total loan portfolio must be greater than zero."
            }

        max_allowed_fldg = portfolio * 0.05
        actual_percentage = (guarantee / portfolio) * 100.0
        is_compliant = guarantee <= max_allowed_fldg

        excess = max(0.0, guarantee - max_allowed_fldg)

        return {
            "compliant": is_compliant,
            "statutory_reference": "RBI/2023-24/53 (Guidelines on Default Loss Guarantee)",
            "max_allowed_percentage": 5.0,
            "actual_percentage": round(actual_percentage, 2),
            "max_allowed_guarantee_inr": round(max_allowed_fldg, 2),
            "actual_guarantee_inr": round(guarantee, 2),
            "excess_amount_inr": round(excess, 2),
            "action_required": "None" if is_compliant else f"Guarantee exceeds statutory 5% cap by INR {excess:,.2f}. Must reduce guarantee or deduct excess 100% from capital."
        }

    def _execute_check_data_localization(self, args: Dict[str, Any]) -> Dict[str, Any]:
        data_cat = args.get("data_category", "")
        region = str(args.get("storage_region", "")).lower()
        is_cross_border = bool(args.get("is_cross_border_transaction", False))

        indian_regions = ["india", "central-india", "south-india", "west-india", "mumbai", "pune", "chennai", "delhi", "hyderabad", "bengaluru", "bangalore"]
        is_stored_in_india = any(k in region for k in indian_regions)
        is_compliant = is_stored_in_india

        return {
            "compliant": is_compliant,
            "statutory_reference": "RBI Circular DPSS.CO.OD.No.2785/06.08.005/2017-18",
            "data_category": data_cat,
            "storage_region": region,
            "onshore_storage_mandated": True,
            "offshore_processing_permitted": is_cross_border,
            "processing_grace_period_hours": 24 if is_cross_border else 0,
            "status": "APPROVED_ONSHORE" if is_compliant else "VIOLATION_OFFSHORE_STORAGE",
            "remediation": "No action required." if is_compliant else "Mandatory: Complete end-to-end payment system data must reside solely in India within 24 hours of offshore processing."
        }

    def _execute_verify_vcip_identity_step(self, args: Dict[str, Any]) -> Dict[str, Any]:
        geo = bool(args.get("live_geotag_in_india", False))
        liveness = bool(args.get("facial_liveness_verified", False))
        aadhaar = bool(args.get("aadhaar_xml_or_digilocker", False))

        failed_checks = []
        if not geo:
            failed_checks.append("Live Geolocation inside India")
        if not liveness:
            failed_checks.append("Automated Facial Liveness Match")
        if not aadhaar:
            failed_checks.append("Offline Aadhaar XML / DigiLocker Verification")

        is_compliant = len(failed_checks) == 0

        return {
            "compliant": is_compliant,
            "statutory_reference": "RBI Master Direction - Know Your Customer (KYC) Direction, 2016 (V-CIP)",
            "failed_checks": failed_checks,
            "mandatory_video_retention_years": 10,
            "status": "V_CIP_VERIFIED" if is_compliant else "V_CIP_REJECTED",
            "action": "Proceed with account opening." if is_compliant else f"Account opening blocked. Missing mandatory V-CIP steps: {', '.join(failed_checks)}"
        }


# Global singleton instance
_global_mcp_bridge: Optional[MCPToolBridge] = None

def get_mcp_bridge() -> MCPToolBridge:
    """Returns or initializes the singleton MCPToolBridge."""
    global _global_mcp_bridge
    if _global_mcp_bridge is None:
        _global_mcp_bridge = MCPToolBridge()
    return _global_mcp_bridge
