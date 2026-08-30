from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.models.entities import User
from app.db.models.entities import RepositoryAnalysis
from app.db.session import get_db
from app.schemas.github import (
    GitHubAnalyzeRequest,
    GitHubAskRequest,
    GitHubAskResponse,
    GitHubRepositoryResponse,
    RepositoryAnalysisResponse,
)
from app.services.github.service import GitHubService
from app.services.oauth import OAuthService

router = APIRouter()


def _analysis_to_response(analysis: RepositoryAnalysis) -> RepositoryAnalysisResponse:
    return RepositoryAnalysisResponse(
        id=analysis.id,
        repository_id=analysis.repository_id,
        summary=analysis.summary,
        architecture=analysis.architecture,
        strengths=analysis.strengths,
        issues=analysis.issues,
        recommendations=analysis.recommendations,
        created_at=analysis.created_at,
    )


@router.post("/analyze", response_model=GitHubRepositoryResponse, status_code=status.HTTP_201_CREATED)
async def analyze_repository(payload: GitHubAnalyzeRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> GitHubRepositoryResponse:
    service = GitHubService(db)
    repository, analysis = await service.analyze_repository(user.id, payload.repository_url)
    return GitHubRepositoryResponse(
        id=repository.id,
        owner=repository.owner,
        name=repository.name,
        url=repository.url,
        languages=repository.languages,
        created_at=repository.created_at,
        latest_analysis=_analysis_to_response(analysis),
    )


@router.get("/connection")
async def github_connection(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    return {"connected": await OAuthService(db).github_connected(user.id)}


@router.get("/available-repositories")
async def available_repositories(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    token = await OAuthService(db).github_token_for_user(user.id)
    if not token:
        raise HTTPException(status_code=400, detail="Connect GitHub to browse your repositories")
    return await GitHubService(db).list_available_repositories(token)


@router.post("/import", response_model=GitHubRepositoryResponse, status_code=status.HTTP_201_CREATED)
async def import_repository(payload: GitHubAnalyzeRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> GitHubRepositoryResponse:
    token = await OAuthService(db).github_token_for_user(user.id)
    if not token:
        raise HTTPException(status_code=400, detail="Connect GitHub before importing a repository")
    try:
        repository, analysis = await GitHubService(db).analyze_repository(user.id, payload.repository_url, token)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not import this GitHub repository") from exc
    return GitHubRepositoryResponse(
        id=repository.id,
        owner=repository.owner,
        name=repository.name,
        url=repository.url,
        languages=repository.languages,
        created_at=repository.created_at,
        latest_analysis=_analysis_to_response(analysis),
    )


@router.get("/repositories", response_model=list[GitHubRepositoryResponse])
async def list_repositories(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> list[GitHubRepositoryResponse]:
    service = GitHubService(db)
    repositories = await service.list_repositories(user.id)
    items: list[GitHubRepositoryResponse] = []
    for repository in repositories:
        result = await db.execute(
            select(RepositoryAnalysis).where(RepositoryAnalysis.repository_id == repository.id).order_by(RepositoryAnalysis.created_at.desc())
        )
        analysis = result.scalars().first()
        items.append(
            GitHubRepositoryResponse(
                id=repository.id,
                owner=repository.owner,
                name=repository.name,
                url=repository.url,
                languages=repository.languages,
                created_at=repository.created_at,
                latest_analysis=_analysis_to_response(analysis) if analysis else None,
            )
        )
    return items


@router.get("/repositories/{repository_id}", response_model=GitHubRepositoryResponse)
async def get_repository(repository_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> GitHubRepositoryResponse:
    service = GitHubService(db)
    repositories = await service.list_repositories(user.id)
    for repository in repositories:
        if str(repository.id) == repository_id:
            result = await db.execute(
                select(RepositoryAnalysis).where(RepositoryAnalysis.repository_id == repository.id).order_by(RepositoryAnalysis.created_at.desc())
            )
            analysis = result.scalars().first()
            return GitHubRepositoryResponse(
                id=repository.id,
                owner=repository.owner,
                name=repository.name,
                url=repository.url,
                languages=repository.languages,
                created_at=repository.created_at,
                latest_analysis=_analysis_to_response(analysis) if analysis else None,
            )
    raise HTTPException(status_code=404, detail="Repository not found")


@router.post("/repositories/{repository_id}/ask", response_model=GitHubAskResponse)
async def ask_repository(repository_id: str, payload: GitHubAskRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> GitHubAskResponse:
    service = GitHubService(db)
    try:
        result = await service.ask_repository_for_user(user.id, repository_id, payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return GitHubAskResponse(answer=result["answer"], sources=result["sources"])
