import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Note
from app.models.transcript import TranscriptSegment
from app.models.number_record import NumberRecord
from app.schemas.note import NoteUpdate, NoteResponse
from app.schemas.transcript import TranscriptSegmentResponse, NumberRecordResponse
from app.services.notes_generator import generate_notes

router = APIRouter(tags=["notes"])


@router.post("/interviews/{interview_id}/notes/generate", response_model=NoteResponse)
async def generate_interview_notes(
    interview_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    note = await generate_notes(db=db, interview_id=interview_id)
    return note


@router.get("/interviews/{interview_id}/notes", response_model=NoteResponse | None)
async def get_notes(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Note).where(Note.interview_id == interview_id)
    )
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Notes not found")
    return note


@router.put("/interviews/{interview_id}/notes", response_model=NoteResponse)
async def update_notes(
    interview_id: uuid.UUID,
    data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Note).where(Note.interview_id == interview_id)
    )
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Notes not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/interviews/{interview_id}/transcript", response_model=list[TranscriptSegmentResponse])
async def get_transcript(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TranscriptSegment)
        .where(TranscriptSegment.interview_id == interview_id)
        .order_by(TranscriptSegment.segment_index)
    )
    return result.scalars().all()


@router.get("/interviews/{interview_id}/numbers", response_model=list[NumberRecordResponse])
async def get_numbers(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NumberRecord)
        .where(NumberRecord.interview_id == interview_id)
        .order_by(NumberRecord.created_at)
    )
    return result.scalars().all()
