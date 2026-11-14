"""Pipeline smoke test for the live in-cluster FastMCP server."""

import asyncio

from app.services.mcp_client import call_regulatory_mcp_tool, list_regulatory_mcp_tools


async def main() -> None:
    tools = await list_regulatory_mcp_tools()
    names = {tool["name"] for tool in tools}
    required = {"search_rbi_regulations", "list_regulatory_domains"}
    missing = required - names
    if missing:
        raise AssertionError(f"MCP server is missing expected tools: {sorted(missing)}")

    domains = await call_regulatory_mcp_tool("list_regulatory_domains", {})
    if not domains or not any("Digital Lending" in domain for domain in domains):
        raise AssertionError("MCP domain-list tool returned unexpected data")

    results = await call_regulatory_mcp_tool(
        "search_rbi_regulations",
        {"query": "digital lending rules for Lending Service Providers", "top_k": 5},
    )
    if not results or not any("digital lending" in item.get("title", "").lower() for item in results):
        raise AssertionError("MCP regulatory search returned no matching RBI result")

    print(f"MCP tools discovered: {sorted(names)}")
    print(f"Regulatory domains returned: {len(domains)}")
    print(f"Matching RBI search results: {len(results)}")


if __name__ == "__main__":
    asyncio.run(main())