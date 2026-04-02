import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    extracted_text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
