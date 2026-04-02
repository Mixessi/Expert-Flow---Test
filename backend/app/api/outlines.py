import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.outline import Outline
from app.schemas.outline import OutlineGenerateRequest, OutlineUpdate, OutlineResponse
from app.services.outline_generator import generate_outline

router = APIRouter(tags=["outlines"])


@router.post("/interviews/{interview_id}/outline/generate", response_model=OutlineResponse)
async def generate_interview_outline(
    interview_id: uuid.UUID,
    data: OutlineGenerateRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    outline = await generate_outline(
        db=db,
        interview_id=interview_id,
        feedback=data.feedback if data else None,
    )
    return outline


@router.get("/interviews/{interview_id}/outline", response_model=OutlineResponse | None)
async def get_active_outline(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Outline).where(
            Outline.interview_id == interview_id,
            Outline.is_active == True,
        )
    )
    outline = result.scalars().first()
    if not outline:
        raise HTTPException(status_code=404, detail="No active outline found")
    return outline


@router.put("/outlines/{outline_id}", response_model=OutlineResponse)
async def update_outline(
    outline_id: uuid.UUID,
    data: OutlineUpdate,
    db: AsyncSession = Depends(get_db),
):
    outline = await db.get(Outline, outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")
    outline.content = data.content
    await db.commit()
    await db.refresh(outline)
    return outline
