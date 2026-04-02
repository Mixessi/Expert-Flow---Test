import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db_types import GUID, JSONType
from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary: Mapped[str | None] = mapped_column(Text)
    key_insights: Mapped[dict | None] = mapped_column(JSONType())
    full_notes: Mapped[str | None] = mapped_column(Text)
    key_numbers: Mapped[dict | None] = mapped_column(JSONType())
    action_items: Mapped[dict | None] = mapped_column(JSONType())
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    interview = relationship("Interview", back_populates="notes")
