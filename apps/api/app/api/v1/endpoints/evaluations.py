from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.evaluation import EvaluationRunResponse
from app.services.evaluation.service import EvaluationService

router = APIRouter()


@router.get("", response_model=list[EvaluationRunResponse])
async def list_evaluations(db: AsyncSession = Depends(get_db)) -> list[EvaluationRunResponse]:
    service = EvaluationService(db)
    return [EvaluationRunResponse.model_validate(item, from_attributes=True) for item in await service.list_runs()]

