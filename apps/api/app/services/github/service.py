from base64 import b64decode
from urllib.parse import urlparse
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.entities import GitHubRepository, RepositoryAnalysis


class GitHubService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()

    async def list_repositories(self, user_id: UUID) -> list[GitHubRepository]:
        result = await self.db.execute(
            select(GitHubRepository).where(GitHubRepository.user_id == user_id).order_by(GitHubRepository.created_at.desc())
        )
        return list(result.scalars())

    async def analyze_repository(self, user_id: UUID, repository_url: str) -> tuple[GitHubRepository, RepositoryAnalysis]:
        owner, name = self._parse_repository_url(repository_url)
        metadata = await self._fetch_repository_data(owner, name)
        repository = GitHubRepository(
            user_id=user_id,
            owner=owner,
            name=name,
            url=repository_url,
            readme=metadata["readme"],
            languages=metadata["languages"],
            file_index=metadata["tree"],
        )
        self.db.add(repository)
        await self.db.flush()
        analysis = RepositoryAnalysis(
            repository_id=repository.id,
            summary=f"{name} is primarily {', '.join(metadata['languages'].keys()) or 'untyped'} and contains {len(metadata['tree'])} indexed paths.",
            architecture="Repository analysis is based on README, language stats, and a filtered directory tree.",
            strengths=[
                "Has a readable repository metadata footprint." if metadata["readme"] else "Repository is accessible through the GitHub API.",
                "Language distribution was collected for contextual analysis.",
            ],
            issues=[
                "Deep source ingestion is intentionally bounded to avoid sending entire repositories to the model.",
                "Commit-level analysis is not yet included in the first pass.",
            ],
            recommendations=[
                "Add richer file sampling and embeddings for code-aware retrieval.",
                "Expand architecture inference with framework heuristics.",
            ],
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(repository)
        await self.db.refresh(analysis)
        return repository, analysis

    async def ask_repository_for_user(self, user_id: UUID, repository_id: UUID, question: str) -> dict:
        result = await self.db.execute(select(GitHubRepository).where(GitHubRepository.id == repository_id, GitHubRepository.user_id == user_id))
        repo = result.scalar_one_or_none()
        if not repo:
            raise ValueError("Repository not found")
        relevant_paths = [entry["path"] for entry in repo.file_index[:5]]
        return {
            "answer": (
                f"Repository question: {question}\n"
                f"Available context includes README length {len(repo.readme)} and sample paths: {', '.join(relevant_paths)}."
            ),
            "sources": [{"path": path} for path in relevant_paths],
        }

    async def _fetch_repository_data(self, owner: str, name: str) -> dict:
        headers = {"Accept": "application/vnd.github+json"}
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            repo_resp = await client.get(f"https://api.github.com/repos/{owner}/{name}", headers=headers)
            repo_resp.raise_for_status()
            languages_resp = await client.get(f"https://api.github.com/repos/{owner}/{name}/languages", headers=headers)
            tree_resp = await client.get(
                f"https://api.github.com/repos/{owner}/{name}/git/trees/HEAD?recursive=1",
                headers=headers,
            )
            readme_resp = await client.get(f"https://api.github.com/repos/{owner}/{name}/readme", headers=headers)
        languages = languages_resp.json() if languages_resp.status_code == 200 else {}
        tree = tree_resp.json().get("tree", []) if tree_resp.status_code == 200 else []
        tree = [{"path": item["path"], "type": item["type"]} for item in tree if item.get("type") == "blob"][:250]
        readme = ""
        if readme_resp.status_code == 200:
            payload = readme_resp.json()
            if payload.get("encoding") == "base64":
                readme = b64decode(payload["content"]).decode("utf-8", errors="ignore")
        return {"languages": languages, "tree": tree, "readme": readme}

    def _parse_repository_url(self, repository_url: str) -> tuple[str, str]:
        parsed = urlparse(repository_url)
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError("Repository URL must look like https://github.com/owner/name")
        return parts[0], parts[1].removesuffix(".git")
