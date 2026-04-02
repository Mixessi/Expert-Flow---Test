from fastapi import APIRouter

from app.api.projects import router as projects_router
from app.api.interviews import router as interviews_router
from app.api.outlines import router as outlines_router
from app.api.notes import router as notes_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router)
api_router.include_router(interviews_router)
api_router.include_router(outlines_router)
api_router.include_router(notes_router)
