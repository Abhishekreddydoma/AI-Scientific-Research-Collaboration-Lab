"""Registry managing all active MCP servers and dispatching tool calls."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.mcp.client import MCPCallResult, MCPServer, MCPToolDefinition


class MCPRegistry:
    """Central registry of all registered MCP servers."""

    def __init__(self):
        self._servers: Dict[str, MCPServer] = {}

    def register_server(self, server: MCPServer) -> None:
        """Add an MCP server to the registry."""
        self._servers[server.name] = server

    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get an MCP server by name."""
        return self._servers.get(name)

    def list_all_tools(self) -> List[MCPToolDefinition]:
        """Aggregate tools across all registered servers."""
        tools = []
        for server in self._servers.values():
            tools.extend(server.list_tools())
        return tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> MCPCallResult:
        """Dispatch a tool call to the specified server."""
        server = self.get_server(server_name)
        if not server:
            return MCPCallResult(
                success=False,
                data=None,
                error=f"MCP Server '{server_name}' not registered",
            )
        return await server.call_tool(tool_name, arguments)


# Global registry instance
mcp_registry = MCPRegistry()
