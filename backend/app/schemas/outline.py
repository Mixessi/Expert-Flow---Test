import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class OutlineGenerateRequest(BaseModel):
    feedback: str | None = None


class OutlineUpdate(BaseModel):
    content: dict[str, Any]


class OutlineResponse(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    version: int
    content: dict[str, Any]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
