"""Client for the in-cluster BankCompliance FastMCP regulatory tools."""

import os
from typing import Any, Dict, List

from fastmcp import Client
from fastmcp.client.transports import SSETransport


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://bankc-mcp-server:8080/sse")
REGULATORY_MCP_TOOLS = {"search_rbi_regulations", "list_regulatory_domains"}


async def list_regulatory_mcp_tools() -> List[Dict[str, Any]]:
    """Discover the regulatory tools from the deployed MCP server."""
    transport = SSETransport(url=MCP_SERVER_URL)
    async with Client(transport, timeout=20.0) as client:
        return [tool.model_dump() for tool in await client.list_tools()]


async def call_regulatory_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Call an allow-listed regulatory tool through the MCP protocol."""
    if tool_name not in REGULATORY_MCP_TOOLS:
        raise ValueError(f"Unsupported regulatory MCP tool: {tool_name}")

    transport = SSETransport(url=MCP_SERVER_URL)
    async with Client(transport, timeout=20.0) as client:
        result = await client.call_tool(tool_name, arguments)
        if getattr(result, "is_error", False):
            raise RuntimeError(f"MCP tool '{tool_name}' returned an error")
        return result.data