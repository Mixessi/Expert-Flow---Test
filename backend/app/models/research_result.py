import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db_types import GUID, JSONType
from app.database import Base


class ResearchResult(Base):
    __tablename__ = "research_results"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    interview_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    company_overview: Mapped[str | None] = mapped_column(Text)
    industry_data: Mapped[str | None] = mapped_column(Text)
    key_numbers: Mapped[dict | None] = mapped_column(JSONType())
    info_gaps: Mapped[dict | None] = mapped_column(JSONType())
    raw_response: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    interview = relationship("Interview", back_populates="research_results")
