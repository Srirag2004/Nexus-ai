from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AgentRunResponse(BaseModel):
    id: UUID
    agent_name: str
    status: str
    input_summary: str
    output_summary: str
    duration_ms: int
    created_at: datetime

