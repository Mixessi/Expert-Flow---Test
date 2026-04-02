import uuid
from datetime import datetime

from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db_types import GUID
from app.database import Base


class NumberRecord(Base):
    __tablename__ = "number_records"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    segment_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("transcript_segments.id"))
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(50))
    context: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    verification: Mapped[str] = mapped_column(String(20), default="unverified")
    flag_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    interview = relationship("Interview", back_populates="number_records")
