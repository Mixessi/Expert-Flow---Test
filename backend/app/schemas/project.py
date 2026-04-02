import uuid
from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    research_goals: str | None = None
    industry: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    research_goals: str | None = None
    industry: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    research_goals: str | None
    industry: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
