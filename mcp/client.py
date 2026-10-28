"""Model Context Protocol (MCP) server & client interface for scientific tools.

Provides a unified protocol for agents to discover, describe, and invoke
tools according to MCP tool calling conventions.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class MCPToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[MCPToolParameter] = Field(default_factory=list)
    server_name: str


class MCPCallResult(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None


class MCPServer:
    """Base class for in-process Model Context Protocol servers."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._tools: Dict[str, Callable[..., Any]] = {}
        self._tool_defs: Dict[str, MCPToolDefinition] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        fn: Callable[..., Any],
        parameters: Optional[List[MCPToolParameter]] = None,
    ) -> None:
        """Register a tool with its schema definition."""
        self._tools[name] = fn
        self._tool_defs[name] = MCPToolDefinition(
            name=name,
            description=description,
            parameters=parameters or [],
            server_name=self.name,
        )

    def list_tools(self) -> List[MCPToolDefinition]:
        """List all available tools exposed by this server."""
        return list(self._tool_defs.values())

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPCallResult:
        """Execute a tool by name with provided arguments."""
        if tool_name not in self._tools:
            return MCPCallResult(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' not found on server '{self.name}'",
            )
        try:
            fn = self._tools[tool_name]
            import inspect
            if inspect.iscoroutinefunction(fn):
                res = await fn(**arguments)
            else:
                res = fn(**arguments)
            return MCPCallResult(success=True, data=res)
        except Exception as e:
            return MCPCallResult(success=False, data=None, error=str(e))
