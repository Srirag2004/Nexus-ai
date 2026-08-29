from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EvaluationRunResponse(BaseModel):
    id: UUID
    evaluation_type: str
    status: str
    metrics: dict
    created_at: datetime

