"""Research result Pydantic schemas."""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ResultType = Literal[
    "literature",
    "dataset",
    "finding",
    "hypothesis",
    "experiment",
    "critique",
    "contradiction",
]


class ResearchResultCreate(BaseModel):
    """Payload required to create a research result."""

    result_type: ResultType = Field(..., description="Category of this result.")
    title: str = Field(..., min_length=1, max_length=500)
    content: dict[str, Any] = Field(
        ...,
        description="Structured result data — serialized to JSON before database storage.",
    )
    source: Optional[str] = Field(None, description="Agent or system that produced this result.")


class ResearchResultResponse(BaseModel):
    """Research result data returned by the API."""

    id: int
    project_id: int
    result_type: str
    title: str
    content: dict[str, Any]
    source: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
