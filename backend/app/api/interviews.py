import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.interview import Interview
from app.models.reference_document import ReferenceDocument
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewResponse
from app.schemas.document import DocumentResponse
from app.schemas.research import ResearchStartRequest, ResearchResponse
from app.services import research_engine, document_service

router = APIRouter(tags=["interviews"])


# --- Interview CRUD ---
@router.post("/projects/{project_id}/interviews", response_model=InterviewResponse)
async def create_interview(
    project_id: uuid.UUID,
    data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
):
    interview = Interview(project_id=project_id, **data.model_dump())
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("/projects/{project_id}/interviews", response_model=list[InterviewResponse])
async def list_interviews(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Interview)
        .where(Interview.project_id == project_id)
        .order_by(Interview.created_at.desc())
    )
    return result.scalars().all()


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.put("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: uuid.UUID,
    data: InterviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(interview, key, value)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.post("/interviews/{interview_id}/start", response_model=InterviewResponse)
async def start_interview(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    interview.status = "live"
    interview.started_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.post("/interviews/{interview_id}/end", response_model=InterviewResponse)
async def end_interview(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    interview.status = "completed"
    interview.ended_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(interview)
    return interview


# --- Research ---
@router.post("/interviews/{interview_id}/research/start", response_model=ResearchResponse)
async def start_research(
    interview_id: uuid.UUID,
    data: ResearchStartRequest,
    db: AsyncSession = Depends(get_db),
):
    interview = await db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    result = await research_engine.run_research(
        db=db,
        interview_id=interview_id,
        query=data.query,
        company=interview.expert_company,
        industry=None,
    )
    return result


@router.get("/interviews/{interview_id}/research", response_model=list[ResearchResponse])
async def get_research(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from app.models.research_result import ResearchResult
    result = await db.execute(
        select(ResearchResult)
        .where(ResearchResult.interview_id == interview_id)
        .order_by(ResearchResult.created_at.desc())
    )
    return result.scalars().all()


# --- Documents ---
@router.post("/interviews/{interview_id}/documents", response_model=DocumentResponse)
async def upload_document(
    interview_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    doc = await document_service.save_document(
        db=db,
        interview_id=interview_id,
        filename=file.filename or "unnamed",
        file_content=content,
        file_type=file.content_type or "application/octet-stream",
    )
    return doc


@router.get("/interviews/{interview_id}/documents", response_model=list[DocumentResponse])
async def list_documents(interview_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReferenceDocument)
        .where(ReferenceDocument.interview_id == interview_id)
        .order_by(ReferenceDocument.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/documents/{document_id}")
async def delete_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    doc = await db.get(ReferenceDocument, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()
    return {"ok": True}
