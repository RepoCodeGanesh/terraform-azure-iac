"""
BankCompliance AI — MCP (Model Context Protocol) Regulatory Search Server (A2)
===============================================================================
Exposes the RBI regulatory search capability as a FastMCP tool that any
MCP-compatible client (Claude Desktop, Cursor, etc.) can call directly.

Architecture:
  - Uses FastMCP (fastmcp>=0.1.0) for ergonomic MCP server definition
  - Wraps the existing QdrantService / search_rbi_clauses function
  - Runs as a standalone process in the bank-compliance namespace
  - Exposed as ClusterIP service `bankc-mcp-server` on port 8080

Running standalone:
    python -m app.services.mcp_server

MCP Tool exposed:
    search_rbi_regulations(query: str, top_k: int = 5) -> list[dict]
    - Searches RBI Master Directions and Circulars for regulatory clauses
    - Returns ranked results with circular_no, title, clause, text, score
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger("BankCompliance-MCP")

try:
    from fastmcp import FastMCP  # type: ignore
except ImportError:
    raise ImportError(
        "fastmcp is required for the MCP server. "
        "Install with: pip install fastmcp>=0.1.0"
    )

# Import the existing regulatory search function
try:
    from app.services.qdrant_service import search_rbi_clauses
    _search_fn = search_rbi_clauses
    logger.info("✅ MCP server using QdrantService for regulatory search")
except ImportError:
    logger.warning("QdrantService not available — MCP server will return empty results")
    _search_fn = None

# ── FastMCP Server Definition ─────────────────────────────────────────────────
mcp = FastMCP(
    name="BankCompliance Regulatory Intelligence",
    instructions=(
        "You are a Banking Regulatory AI assistant with access to RBI Master Directions "
        "and Circulars. Use search_rbi_regulations to find precise regulatory clauses "
        "before answering any Indian banking compliance question."
    ),
)


@mcp.tool()
async def search_rbi_regulations(query: str, top_k: int = 5) -> list[dict]:
    """
    Search RBI Master Directions and Circulars for regulatory clauses relevant to
    the compliance query.

    Args:
        query:  The compliance question or regulatory topic to search for.
                Examples: "KYC for NRI accounts", "data localization cloud banking",
                "card tokenization CoFT rules", "digital lending FLDG"
        top_k:  Maximum number of regulatory clauses to return (default: 5, max: 10)

    Returns:
        List of matching regulatory clauses, each with:
        - circular_no:   RBI Circular / Master Direction reference
        - title:         Master Direction title
        - clause:        Specific section / clause identifier
        - text:          Full clause text
        - score:         Relevance score (0.0–1.0, higher is more relevant)
    """
    if _search_fn is None:
        logger.error("search_rbi_clauses not available — returning empty results")
        return []

    # Clamp top_k to sane bounds
    top_k = max(1, min(int(top_k), 10))

    try:
        results = await _search_fn(query=query, limit=top_k)
        return [
            {
                "circular_no": r.get("circular_no", ""),
                "title":       r.get("title", ""),
                "clause":      r.get("clause", ""),
                "text":        r.get("text", ""),
                "score":       round(float(r.get("score", 0.0)), 4),
            }
            for r in results
        ]
    except Exception as exc:
        logger.error("MCP search_rbi_regulations failed: %s", exc)
        return []


@mcp.tool()
async def list_regulatory_domains() -> list[str]:
    """
    Returns the list of regulatory domains covered by BankCompliance AI.
    Use this to understand what topics are searchable before calling
    search_rbi_regulations.

    Returns:
        List of regulatory domain names covered by the knowledge base.
    """
    return [
        "KYC & Customer Due Diligence (V-CIP, OVD, CKYCR)",
        "IT Governance & Cybersecurity (Data Localization, MeitY Cloud Policy)",
        "IT Outsourcing & Vendor Risk Management (CISO, SOC-2, Core Banking)",
        "Digital Payment Security & Card Tokenization (CoFT, TSP, PAN Storage)",
        "Digital Lending Guidelines (FLDG, Cooling-off Periods, DLA Regulations)",
        "Anti-Money Laundering (PMLA, CDD, Beneficial Ownership)",
        "Prudential Norms & Capital Adequacy (Basel III, CRAR, LCR)",
        "Interest Rate Risk & Liquidity Risk Management",
        "Customer Protection & Fair Practices Code",
        "NBFC Regulatory Framework & Compliance Reporting",
    ]


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    logger.info("Starting BankCompliance MCP Server (transport=%s)", transport)
    mcp.run(transport=transport)
