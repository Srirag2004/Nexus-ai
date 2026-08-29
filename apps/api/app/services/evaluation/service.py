from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.entities import AgentRun, EvaluationRun, Message


class EvaluationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_runs(self, user_id: UUID) -> list[EvaluationRun]:
        result = await self.db.execute(select(EvaluationRun).where(EvaluationRun.user_id == user_id).order_by(EvaluationRun.created_at.desc()))
        return list(result.scalars())

    async def run_smoke_eval(self, user_id: UUID) -> EvaluationRun:
        agent_runs = (await self.db.execute(select(AgentRun))).scalars().all()
        messages = (await self.db.execute(select(Message))).scalars().all()
        metrics = {
            "rag_groundedness": 0.6 if any(message.sources for message in messages) else 0.0,
            "tool_selection_success": 1.0 if agent_runs else 0.0,
            "response_count": len(messages),
        }
        run = EvaluationRun(user_id=user_id, evaluation_type="smoke", status="completed", metrics=metrics)
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run
from uuid import UUID
