from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.entities import AgentRun
from app.db.session import get_db
from app.schemas.agent import AgentRunResponse

router = APIRouter()


@router.get("/runs", response_model=list[AgentRunResponse])
async def list_agent_runs(db: AsyncSession = Depends(get_db)) -> list[AgentRunResponse]:
    result = await db.execute(select(AgentRun).order_by(AgentRun.created_at.desc()))
    return [AgentRunResponse.model_validate(item, from_attributes=True) for item in result.scalars()]

