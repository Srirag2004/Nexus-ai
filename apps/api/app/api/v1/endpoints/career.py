from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.models.entities import User
from app.db.session import get_db
from app.schemas.career import CareerAnalyzeRequest, CareerAnalysisResponse
from app.services.career.service import CareerService

router = APIRouter()


@router.post("/analyze", response_model=CareerAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_career(payload: CareerAnalyzeRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> CareerAnalysisResponse:
    service = CareerService(db)
    analysis = await service.analyze(user.id, payload)
    return CareerAnalysisResponse(
        id=analysis.id,
        match_score=analysis.match_score,
        matched_skills=analysis.matched_skills,
        missing_skills=analysis.missing_skills,
        recommendations=analysis.recommendations,
        summary=analysis.summary,
        created_at=analysis.created_at,
    )
