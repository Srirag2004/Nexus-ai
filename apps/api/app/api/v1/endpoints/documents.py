from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.document import DocumentAskRequest, DocumentAskResponse, DocumentResponse
from app.services.rag.service import DocumentService
from app.utils.text import slugify_filename

router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[DocumentResponse]:
    service = DocumentService(db)
    documents = await service.list_documents(get_settings().default_user_id)
    return [
        DocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            status=document.status,
            created_at=document.created_at,
            metadata=document.metadata_json,
        )
        for document in documents
    ]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> DocumentResponse:
    payload = await file.read()
    max_size = get_settings().max_upload_size_mb * 1024 * 1024
    if len(payload) > max_size:
        raise HTTPException(status_code=413, detail="Upload is too large")
    try:
        service = DocumentService(db)
        document = await service.ingest_document(
            get_settings().default_user_id,
            slugify_filename(file.filename or "document.txt"),
            file.content_type or "application/octet-stream",
            payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        status=document.status,
        created_at=document.created_at,
        metadata=document.metadata_json,
    )


@router.post("/ask", response_model=DocumentAskResponse)
async def ask_documents(payload: DocumentAskRequest, db: AsyncSession = Depends(get_db)) -> DocumentAskResponse:
    service = DocumentService(db)
    return await service.ask(get_settings().default_user_id, payload.question, payload.top_k)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)) -> None:
    service = DocumentService(db)
    await service.delete_document(get_settings().default_user_id, document_id)

