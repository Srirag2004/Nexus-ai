from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GitHubAnalyzeRequest(BaseModel):
    repository_url: str = Field(min_length=1)


class GitHubAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class RepositoryAnalysisResponse(BaseModel):
    id: UUID
    repository_id: UUID
    summary: str
    architecture: str
    strengths: list[str]
    issues: list[str]
    recommendations: list[str]
    created_at: datetime


class GitHubRepositoryResponse(BaseModel):
    id: UUID
    owner: str
    name: str
    url: str
    languages: dict
    created_at: datetime
    latest_analysis: RepositoryAnalysisResponse | None = None


class GitHubAskResponse(BaseModel):
    answer: str
    sources: list[dict]

