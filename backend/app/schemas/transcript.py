import uuid
from datetime import datetime

from pydantic import BaseModel


class TranscriptSegmentResponse(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    segment_index: int
    speaker: str | None
    text: str
    start_time_ms: int
    end_time_ms: int
    confidence: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NumberRecordResponse(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    value: str
    normalized: float | None
    unit: str | None
    context: str | None
    category: str | None
    verification: str
    flag_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
