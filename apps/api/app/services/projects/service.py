from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.entities import Document, GitHubRepository, Project, ProjectDocument, RepositoryAnalysis
from app.schemas.project import ProjectCreate
from app.services.ai.base import AIProvider


class ProjectService:
    def __init__(self, db: AsyncSession, provider: AIProvider) -> None:
        self.db = db
        self.provider = provider

    async def list_projects(self, user_id: UUID) -> list[Project]:
        result = await self.db.execute(select(Project).where(Project.user_id == user_id).order_by(Project.updated_at.desc()))
        return list(result.scalars())

    async def get_project(self, user_id: UUID, project_id: UUID) -> Project | None:
        result = await self.db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_project(self, user_id: UUID, payload: ProjectCreate) -> Project:
        if payload.repository_id:
            repository = await self._repository_for_user(user_id, payload.repository_id)
            if repository is None:
                raise ValueError("Selected repository was not found in your workspace")
        documents = await self._documents_for_user(user_id, payload.document_ids)
        if len(documents) != len(set(payload.document_ids)):
            raise ValueError("One or more selected knowledge files were not found in your workspace")

        project = Project(
            user_id=user_id,
            title=payload.title.strip(),
            goal=payload.goal.strip(),
            description=payload.description.strip(),
        )
        if payload.repository_id:
            project.repository_id = payload.repository_id
        self.db.add(project)
        await self.db.flush()
        for document in documents:
            self.db.add(ProjectDocument(project_id=project.id, document_id=document.id))
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def generate_brief(self, user_id: UUID, project_id: UUID) -> Project:
        project = await self.get_project(user_id, project_id)
        if project is None:
            raise ValueError("Project not found")
        repository = await self._repository_for_user(user_id, project.repository_id) if project.repository_id else None
        documents = await self.documents_for_project(project.id, user_id)
        repository_analysis = await self._latest_repository_analysis(repository.id) if repository else None
        context = self._context(project, repository, repository_analysis, documents)
        fallback = self._fallback_brief(project, repository, documents)
        try:
            project.brief = await self.provider.generate(
                "You are NEXUS Project Intelligence. Write one concise, practical project brief in two short paragraphs. "
                "State the project outcome, the available evidence, and the most useful execution focus. Do not invent facts.",
                context,
            )
        except Exception:
            project.brief = fallback
        project.milestones = self._milestones(project, repository, documents)
        project.risks = self._risks(repository_analysis, documents)
        project.next_steps = self._next_steps(project, repository, documents)
        project.status = "active"
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def documents_for_project(self, project_id: UUID, user_id: UUID) -> list[Document]:
        result = await self.db.execute(
            select(Document)
            .join(ProjectDocument, ProjectDocument.document_id == Document.id)
            .where(ProjectDocument.project_id == project_id, Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars())

    async def _repository_for_user(self, user_id: UUID, repository_id: UUID | None) -> GitHubRepository | None:
        if repository_id is None:
            return None
        result = await self.db.execute(select(GitHubRepository).where(GitHubRepository.id == repository_id, GitHubRepository.user_id == user_id))
        return result.scalar_one_or_none()

    async def _documents_for_user(self, user_id: UUID, document_ids: list[UUID]) -> list[Document]:
        if not document_ids:
            return []
        result = await self.db.execute(select(Document).where(Document.user_id == user_id, Document.id.in_(set(document_ids))))
        return list(result.scalars())

    async def _latest_repository_analysis(self, repository_id: UUID) -> RepositoryAnalysis | None:
        result = await self.db.execute(
            select(RepositoryAnalysis)
            .where(RepositoryAnalysis.repository_id == repository_id)
            .order_by(RepositoryAnalysis.created_at.desc())
        )
        return result.scalars().first()

    @staticmethod
    def _context(project: Project, repository: GitHubRepository | None, analysis: RepositoryAnalysis | None, documents: list[Document]) -> str:
        parts = [f"Project: {project.title}", f"Goal: {project.goal}"]
        if project.description:
            parts.append(f"Notes: {project.description}")
        if repository:
            parts.append(f"Repository: {repository.owner}/{repository.name}; languages: {', '.join(repository.languages.keys()) or 'unknown'}")
        if analysis:
            parts.append(f"Repository analysis: {analysis.summary}")
            parts.append(f"Known issues: {', '.join(analysis.issues[:3])}")
        if documents:
            parts.append("Knowledge files: " + ", ".join(document.filename for document in documents))
        return "\n".join(parts)

    @staticmethod
    def _fallback_brief(project: Project, repository: GitHubRepository | None, documents: list[Document]) -> str:
        sources = []
        if repository:
            sources.append(f"the linked {repository.name} repository")
        if documents:
            sources.append(f"{len(documents)} knowledge file{'s' if len(documents) != 1 else ''}")
        evidence = " and ".join(sources) if sources else "your project goal and notes"
        return f"{project.title} is focused on {project.goal}. NEXUS will use {evidence} as the working context.\n\nStart by defining the smallest outcome you can show, then turn the next steps into visible progress."

    @staticmethod
    def _milestones(project: Project, repository: GitHubRepository | None, documents: list[Document]) -> list[str]:
        milestones = [f"Define a measurable first outcome for: {project.goal}"]
        if repository:
            milestones.append(f"Review {repository.name} and turn its architecture into a short execution backlog")
        if documents:
            milestones.append("Extract decisions and requirements from the linked knowledge files")
        milestones.append("Ship a small, testable milestone and record the result")
        return milestones[:4]

    @staticmethod
    def _risks(analysis: RepositoryAnalysis | None, documents: list[Document]) -> list[str]:
        risks = list(analysis.issues[:2]) if analysis else []
        if not documents:
            risks.append("No knowledge files are linked, so the brief has limited supporting context.")
        if not risks:
            risks.append("Validate the project goal with a small user or technical test before expanding scope.")
        return risks[:3]

    @staticmethod
    def _next_steps(project: Project, repository: GitHubRepository | None, documents: list[Document]) -> list[str]:
        steps = ["Write the first outcome as a one-sentence success metric."]
        if repository:
            steps.append(f"Open {repository.name} and create the first implementation task.")
        if documents:
            steps.append("Review the linked files and capture the most important decision or requirement.")
        steps.append("Return here after progress to refresh the project brief.")
        return steps[:3]
