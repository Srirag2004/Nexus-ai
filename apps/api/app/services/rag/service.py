from io import BytesIO
from uuid import UUID

from pypdf import PdfReader
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.entities import Document, DocumentChunk
from app.schemas.document import DocumentAskResponse
from app.utils.text import chunk_text, cosine_similarity, simple_embedding


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_documents(self, user_id: UUID) -> list[Document]:
        result = await self.db.execute(select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc()))
        return list(result.scalars())

    async def ingest_document(self, user_id: UUID, filename: str, content_type: str, payload: bytes) -> Document:
        text_content = self._extract_text(filename, content_type, payload)
        document = Document(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            status="ready",
            text_content=text_content,
            metadata_json={"length": len(text_content)},
        )
        self.db.add(document)
        await self.db.flush()
        chunks = chunk_text(text_content)
        for index, chunk in enumerate(chunks):
            self.db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    source_ref=f"{filename}#chunk-{index + 1}",
                    embedding=simple_embedding(chunk),
                    metadata_json={"chunk_index": index},
                )
            )
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete_document(self, user_id: UUID, document_id: UUID) -> None:
        await self.db.execute(delete(Document).where(Document.user_id == user_id, Document.id == document_id))
        await self.db.commit()

    async def ask(self, user_id: UUID, question: str, top_k: int = 4) -> DocumentAskResponse:
        result = await self.db.execute(
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == user_id)
        )
        rows = list(result.all())
        query_embedding = simple_embedding(question)
        ranked = sorted(
            rows,
            key=lambda row: cosine_similarity(row[0].embedding or [], query_embedding),
            reverse=True,
        )[:top_k]
        if not ranked:
            return DocumentAskResponse(answer="No knowledge documents are available yet.", sources=[])
        sources = [
            {
                "document_id": str(document.id),
                "filename": document.filename,
                "source_ref": chunk.source_ref,
                "snippet": chunk.content[:180],
            }
            for chunk, document in ranked
        ]
        answer = "Grounded summary based on uploaded documents:\n" + "\n".join(
            f"- {source['filename']}: {source['snippet']}" for source in sources
        )
        return DocumentAskResponse(answer=answer, sources=sources)

    def _extract_text(self, filename: str, content_type: str, payload: bytes) -> str:
        suffix = filename.lower().split(".")[-1]
        if suffix in {"txt", "md"} or content_type.startswith("text/"):
            return payload.decode("utf-8", errors="ignore")
        if suffix == "pdf" or content_type == "application/pdf":
            reader = PdfReader(BytesIO(payload))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        raise ValueError("Unsupported document type. Use PDF, TXT, or Markdown.")

