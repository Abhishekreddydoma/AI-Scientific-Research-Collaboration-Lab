"""Scientific search MCP server."""

from __future__ import annotations

from typing import Any, Dict, List
from app.mcp.client import MCPServer, MCPToolParameter
from app.tools.literature.service import literature_search_service


def create_scientific_search_server() -> MCPServer:
    server = MCPServer(
        name="scientific_search_server",
        description="Search peer-reviewed literature, papers, citations, and abstracts",
    )

    async def search_papers(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        papers = await literature_search_service.search(query=query, limit=limit)
        return [p.model_dump() for p in papers]

    server.register_tool(
        name="search_papers",
        description="Search for relevant peer-reviewed scientific papers by keyword query",
        fn=search_papers,
        parameters=[
            MCPToolParameter(name="query", type="string", description="Scientific search query"),
            MCPToolParameter(name="limit", type="integer", description="Maximum papers to return", required=False, default=5),
        ],
    )

    return server
