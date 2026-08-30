from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import get_current_user
from app.db.models.entities import User
from app.db.session import get_db
from app.schemas.career import CareerAnalyzeRequest, CareerAnalysisResponse
from app.services.career.service import CareerService
from app.services.rag.service import DocumentService

router = APIRouter()


@router.post("/analyze", response_model=CareerAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_career(payload: CareerAnalyzeRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> CareerAnalysisResponse:
    service = CareerService(db)
    analysis = await service.analyze(user.id, payload)
    return _response(analysis)


@router.post("/analyze-upload", response_model=CareerAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_career_upload(
    resume_text: str = Form(""),
    job_description: str = Form(""),
    resume_file: UploadFile | None = File(None),
    job_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CareerAnalysisResponse:
    resume_content = await _read_source("resume", resume_text, resume_file)
    job_content = await _read_source("job description", job_description, job_file)
    service = CareerService(db)
    analysis = await service.analyze(user.id, CareerAnalyzeRequest(resume_text=resume_content, job_description=job_content))
    return _response(analysis)


async def _read_source(label: str, pasted_text: str, uploaded_file: UploadFile | None) -> str:
    content = pasted_text.strip()
    if uploaded_file is not None and uploaded_file.filename:
        payload = await uploaded_file.read()
        max_size = get_settings().max_upload_size_mb * 1024 * 1024
        if len(payload) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"The {label} file is too large. Maximum size is {get_settings().max_upload_size_mb} MB.",
            )
        try:
            extracted = DocumentService.extract_text(uploaded_file.filename, uploaded_file.content_type or "", payload).strip()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        content = "\n\n".join(part for part in (content, extracted) if part)
    if not content:
        raise HTTPException(status_code=400, detail=f"Add {label} text or upload a file before analyzing.")
    return content


def _response(analysis) -> CareerAnalysisResponse:
    return CareerAnalysisResponse(
        id=analysis.id,
        match_score=analysis.match_score,
        matched_skills=analysis.matched_skills,
        missing_skills=analysis.missing_skills,
        recommendations=analysis.recommendations,
        summary=analysis.summary,
        created_at=analysis.created_at,
    )
