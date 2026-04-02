import uuid
from datetime import datetime

from pydantic import BaseModel


class InterviewCreate(BaseModel):
    expert_name: str | None = None
    expert_title: str | None = None
    expert_company: str | None = None
    expert_bio: str | None = None
    core_questions: str | None = None
    scheduled_at: datetime | None = None


class InterviewUpdate(BaseModel):
    expert_name: str | None = None
    expert_title: str | None = None
    expert_company: str | None = None
    expert_bio: str | None = None
    core_questions: str | None = None
    scheduled_at: datetime | None = None


class InterviewResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    expert_name: str | None
    expert_title: str | None
    expert_company: str | None
    expert_bio: str | None
    core_questions: str | None
    status: str
    scheduled_at: datetime | None
    started_at: datetime | None
    ended_at: datetime | None
    credibility_score: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
