"""Research report Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResearchReportCreate(BaseModel):
    """Payload required to create a research report."""

    report_content: str = Field(
        ...,
        min_length=1,
        description="Full text content of the research report.",
    )


class ResearchReportResponse(BaseModel):
    """Research report data returned by the API."""

    id: int
    project_id: int
    report_content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
