"""Client for the in-cluster BankCompliance FastMCP regulatory tools."""

import dataclasses
import json
import logging
import os
from typing import Any, Dict, List

from fastmcp import Client
from fastmcp.client.transports import SSETransport

logger = logging.getLogger("BankCompliance-MCPClient")

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://bankc-mcp-server:8080/sse")
REGULATORY_MCP_TOOLS = {"search_rbi_regulations", "list_regulatory_domains"}


def _serialize_mcp_item(item: Any) -> Any:
    """Recursively convert FastMCP/Pydantic/dataclass item to pure Python primitives."""
    if isinstance(item, dict):
        return {k: _serialize_mcp_item(v) for k, v in item.items()}
    if isinstance(item, list):
        return [_serialize_mcp_item(v) for v in item]
    if hasattr(item, "model_dump"):
        return item.model_dump()
    if dataclasses.is_dataclass(item):
        return dataclasses.asdict(item)
    if hasattr(item, "__dict__") and getattr(item, "__dict__"):
        return {k: _serialize_mcp_item(v) for k, v in item.__dict__.items() if not k.startswith("_")}
    return item


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

        # 1. Prefer structured_content['result'] provided by FastMCP 2.x
        if hasattr(result, "structured_content") and isinstance(result.structured_content, dict) and "result" in result.structured_content:
            return _serialize_mcp_item(result.structured_content["result"])

        # 2. Check for text content containing serialized JSON
        if getattr(result, "content", None):
            for c in result.content:
                if getattr(c, "type", "") == "text" and c.text:
                    try:
                        parsed = json.loads(c.text)
                        return _serialize_mcp_item(parsed)
                    except Exception:
                        pass

        # 3. Fallback to result.data converted to dict/primitives
        return _serialize_mcp_item(result.data)
