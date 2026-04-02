import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ResearchStartRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    query: str
    status: str
    company_overview: str | None
    industry_data: str | None
    key_numbers: list[dict[str, Any]] | None
    info_gaps: list[str] | None
    created_at: datetime

    model_config = {"from_attributes": True}
