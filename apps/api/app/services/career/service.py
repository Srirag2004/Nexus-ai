from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.entities import CareerAnalysis, GitHubRepository, Memory
from app.schemas.career import CareerAnalyzeRequest


class CareerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def analyze(self, user_id: UUID, payload: CareerAnalyzeRequest) -> CareerAnalysis:
        repo_result = await self.db.execute(select(GitHubRepository).where(GitHubRepository.user_id == user_id))
        memory_result = await self.db.execute(select(Memory).where(Memory.user_id == user_id))
        repository_terms = {repo.name.lower() for repo in repo_result.scalars()}
        memory_terms = {memory.category.lower() for memory in memory_result.scalars()}
        resume_terms = set(payload.resume_text.lower().split())
        job_terms = set(payload.job_description.lower().split())
        matched = sorted(term for term in job_terms if term in resume_terms)[:12]
        missing = sorted(term for term in job_terms if term not in resume_terms and len(term) > 4)[:12]
        score = round(min(0.95, (len(matched) + len(repository_terms & job_terms) + len(memory_terms & job_terms)) / 20), 2)
        analysis = CareerAnalysis(
            user_id=user_id,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            match_score=score,
            matched_skills=matched,
            missing_skills=missing,
            recommendations=[
                "Strengthen project bullets with measurable backend or AI outcomes.",
                "Add evidence for the most important missing skills using a project, certification, or focused learning sprint.",
                "Use repository and memory context to tailor the resume summary to the target role.",
            ],
            summary="NEXUS generated a heuristic career fit summary using resume text, job text, stored memories, and indexed repositories.",
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

