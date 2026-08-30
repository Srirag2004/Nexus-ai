from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.models.entities import Project, User
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.ai.factory import get_ai_provider
from app.services.projects.service import ProjectService

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> list[ProjectResponse]:
    service = ProjectService(db, get_ai_provider())
    projects = await service.list_projects(user.id)
    return [await _to_response(project, service, user.id) for project in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> ProjectResponse:
    service = ProjectService(db, get_ai_provider())
    try:
        project = await service.create_project(user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return await _to_response(project, service, user.id)


@router.post("/{project_id}/generate", response_model=ProjectResponse)
async def generate_project_brief(project_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> ProjectResponse:
    service = ProjectService(db, get_ai_provider())
    try:
        project = await service.generate_brief(user.id, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return await _to_response(project, service, user.id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    service = ProjectService(db, get_ai_provider())
    project = await service.get_project(user.id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()


async def _to_response(project: Project, service: ProjectService, user_id: UUID) -> ProjectResponse:
    repository = await service._repository_for_user(user_id, project.repository_id)
    documents = await service.documents_for_project(project.id, user_id)
    return ProjectResponse(
        id=project.id,
        title=project.title,
        goal=project.goal,
        description=project.description,
        status=project.status,
        repository_id=project.repository_id,
        repository_name=f"{repository.owner}/{repository.name}" if repository else None,
        document_ids=[document.id for document in documents],
        document_names=[document.filename for document in documents],
        brief=project.brief,
        milestones=project.milestones,
        risks=project.risks,
        next_steps=project.next_steps,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )
