import uuid
from datetime import datetime

from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db_types import GUID
from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    expert_name: Mapped[str | None] = mapped_column(String(255))
    expert_title: Mapped[str | None] = mapped_column(String(255))
    expert_company: Mapped[str | None] = mapped_column(String(255))
    expert_bio: Mapped[str | None] = mapped_column(Text)
    core_questions: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    credibility_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="interviews")
    outlines = relationship("Outline", back_populates="interview", cascade="all, delete-orphan")
    transcript_segments = relationship("TranscriptSegment", back_populates="interview", cascade="all, delete-orphan")
    number_records = relationship("NumberRecord", back_populates="interview", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="interview", cascade="all, delete-orphan")
    research_results = relationship("ResearchResult", back_populates="interview", cascade="all, delete-orphan")
    reference_documents = relationship("ReferenceDocument", back_populates="interview", cascade="all, delete-orphan")
