"""Data and statistics MCP server."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.mcp.client import MCPServer, MCPToolParameter
from app.tools.data.datasets import get_dataset
from app.tools.statistics.analysis import compute_descriptive_stats, compute_correlation, run_ols_regression


def create_data_tools_server() -> MCPServer:
    server = MCPServer(
        name="data_tools_server",
        description="Dataset inspection, statistical hypothesis testing, correlation and regression tools",
    )

    def describe_dataset() -> Dict[str, Any]:
        df = get_dataset()
        stats = compute_descriptive_stats(df)
        return {
            "num_records": len(df),
            "columns": list(df.columns),
            "statistics": {col: s.model_dump() for col, s in stats.items()},
        }

    def run_correlation(var_x: str, var_y: str) -> Dict[str, Any]:
        df = get_dataset()
        res = compute_correlation(df, var_x, var_y)
        return res.model_dump()

    def run_regression(
        dependent_var: str,
        independent_vars: List[str],
        formula: Optional[str] = None,
    ) -> Dict[str, Any]:
        df = get_dataset()
        res = run_ols_regression(df, dependent_var, independent_vars, formula)
        return res.model_dump()

    server.register_tool(
        name="describe_dataset",
        description="Get full descriptive statistical summary for all numerical variables in the research dataset",
        fn=describe_dataset,
    )

    server.register_tool(
        name="run_correlation",
        description="Compute Pearson and Spearman correlation between two continuous variables with p-values",
        fn=run_correlation,
        parameters=[
            MCPToolParameter(name="var_x", type="string", description="First variable name"),
            MCPToolParameter(name="var_y", type="string", description="Second variable name"),
        ],
    )

    server.register_tool(
        name="run_regression",
        description="Fit an Ordinary Least Squares (OLS) regression model and return R-squared, F-stat, coefficients, and p-values",
        fn=run_regression,
        parameters=[
            MCPToolParameter(name="dependent_var", type="string", description="Target dependent variable (Y)"),
            MCPToolParameter(name="independent_vars", type="array", description="List of predictor variables (X)"),
            MCPToolParameter(name="formula", type="string", description="Optional statsmodels R-style formula", required=False),
        ],
    )

    return server
