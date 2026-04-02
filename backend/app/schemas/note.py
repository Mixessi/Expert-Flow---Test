import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class NoteUpdate(BaseModel):
    summary: str | None = None
    full_notes: str | None = None


class NoteResponse(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    summary: str | None
    key_insights: list[dict[str, Any]] | None
    full_notes: str | None
    key_numbers: list[dict[str, Any]] | None
    action_items: list[dict[str, Any]] | None
    generated_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
