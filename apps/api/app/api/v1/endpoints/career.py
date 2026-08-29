from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.career import CareerAnalyzeRequest, CareerAnalysisResponse
from app.services.career.service import CareerService

router = APIRouter()


@router.post("/analyze", response_model=CareerAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_career(payload: CareerAnalyzeRequest, db: AsyncSession = Depends(get_db)) -> CareerAnalysisResponse:
    service = CareerService(db)
    analysis = await service.analyze(get_settings().default_user_id, payload)
    return CareerAnalysisResponse(
        id=analysis.id,
        match_score=analysis.match_score,
        matched_skills=analysis.matched_skills,
        missing_skills=analysis.missing_skills,
        recommendations=analysis.recommendations,
        summary=analysis.summary,
        created_at=analysis.created_at,
    )

