"""MCP Servers initialization and registry setup."""

from app.mcp.registry import mcp_registry
from app.mcp.servers.scientific_search import create_scientific_search_server
from app.mcp.servers.data_tools import create_data_tools_server
from app.mcp.servers.research_knowledge import create_research_knowledge_server


def setup_default_mcp_servers():
    """Register all core in-process scientific MCP servers."""
    mcp_registry.register_server(create_scientific_search_server())
    mcp_registry.register_server(create_data_tools_server())
    mcp_registry.register_server(create_research_knowledge_server())


__all__ = [
    "setup_default_mcp_servers",
    "create_scientific_search_server",
    "create_data_tools_server",
    "create_research_knowledge_server",
]
