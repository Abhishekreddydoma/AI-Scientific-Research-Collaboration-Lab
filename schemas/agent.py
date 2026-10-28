"""Agent Pydantic schemas.

These models define the contract for agent tasks and results, as well as
A2A communication contracts.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

AgentRunStatus = Literal["pending", "running", "completed", "failed"]


class AgentTask(BaseModel):
    """Describes a task to be executed by a research agent."""

    task_id: str = Field(default_factory=lambda: "task-001")
    project_id: Optional[int] = 1
    agent_name: str = "research_lead"
    objective: Optional[str] = "Conduct scientific investigation"
    context: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class AgentResult(BaseModel):
    """Result returned by a research agent after task execution."""

    task_id: str
    agent_name: str
    status: str = "completed"
    summary: Optional[str] = None
    output_data: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    artifacts: List[Any] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class AgentRunResponse(BaseModel):
    """Agent run record returned by the API."""

    id: int
    project_id: int
    agent_name: str
    status: str
    input: Optional[str] = None
    output: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
