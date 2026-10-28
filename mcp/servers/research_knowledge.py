"""Research knowledge MCP server for cross-referencing findings and identifying contradictions."""

from __future__ import annotations

from typing import Any, Dict, List
from app.mcp.client import MCPServer, MCPToolParameter
from app.tools.literature.corpus import URBAN_HEAT_ISLAND_CORPUS


def create_research_knowledge_server() -> MCPServer:
    server = MCPServer(
        name="research_knowledge_server",
        description="Access foundational scientific domain knowledge, domain baselines, and cross-reference literature",
    )

    def get_known_literature_baselines() -> List[Dict[str, Any]]:
        """Return established consensus metrics from literature."""
        return [
            {
                "relationship": "NDVI vs LST (Surface Temperature)",
                "expected_sign": "negative",
                "typical_pearson_range": [-0.80, -0.45],
                "moderators": ["tree_canopy_pct", "impervious_surface_pct", "albedo"],
                "citation": "Weng et al. (2004), Voogt & Oke (2003)",
            },
            {
                "relationship": "Impervious Surface vs LST",
                "expected_sign": "positive",
                "typical_pearson_range": [0.60, 0.85],
                "moderators": ["albedo", "vegetation_cover"],
                "citation": "Imhoff et al. (2010)",
            },
            {
                "relationship": "Albedo vs LST",
                "expected_sign": "negative",
                "typical_pearson_range": [-0.50, -0.20],
                "moderators": ["surface_material", "solar_radiation"],
                "citation": "Akbari et al. (2001)",
            },
        ]

    server.register_tool(
        name="get_literature_baselines",
        description="Retrieve domain consensus findings, typical effect sizes, and theoretical baselines for cross-verification",
        fn=get_known_literature_baselines,
    )

    return server
