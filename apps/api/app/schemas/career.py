from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CareerAnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    job_description: str = Field(min_length=1)


class CareerAnalysisResponse(BaseModel):
    id: UUID
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    recommendations: list[str]
    summary: str
    created_at: datetime
    heuristic: str = "Heuristic match score, not a scientific assessment."

