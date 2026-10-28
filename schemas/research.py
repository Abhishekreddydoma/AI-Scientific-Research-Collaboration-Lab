"""Research project Pydantic schemas."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Literal union keeps status values in one place
ProjectStatus = Literal["created", "running", "completed", "failed", "paused"]


class ResearchCreate(BaseModel):
    """Payload required to create a research project."""

    title: str = Field(..., min_length=1, max_length=500, description="Short descriptive title.")
    research_question: str = Field(
        ...,
        min_length=10,
        description="The primary research question this project aims to answer.",
    )
    user_id: int = Field(..., description="ID of the user who owns this project.")


class ResearchUpdate(BaseModel):
    """Partial update payload for a research project.

    All fields are optional; only provided fields are updated.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    research_question: Optional[str] = Field(None, min_length=10)
    status: Optional[ProjectStatus] = None


class ResearchResponse(BaseModel):
    """Research project data returned by the API."""

    id: int
    user_id: int
    title: str
    research_question: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
