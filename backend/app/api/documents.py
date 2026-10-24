"""IF-02, IF-03, IF-04: tải lên, danh sách, chi tiết, thử lại, xóa tài liệu (US-001..007)."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_runtime
from app.api.security import require_role
from app.modules.access.service import ROLE_BD, ROLE_SECURITY_ADMIN, CurrentUser
from app.modules.documents import service
from app.modules.documents.models import Document

router = APIRouter(prefix="/documents", tags=["documents"])

bd_only = require_role(ROLE_BD)


class UploadResultOut(BaseModel):
    id: uuid.UUID | None
    file_name: str
    status: str
    failure_reason: str | None = None


class DocumentOut(BaseModel):
    id: uuid.UUID
    file_name: str
    size_bytes: int
    page_count: int | None
    status: str
    failure_reason: str | None
    uploaded_at: datetime


def to_out(doc: Document) -> DocumentOut:
    return DocumentOut(
        id=doc.id,
        file_name=doc.file_name,
        size_bytes=doc.size_bytes,
        page_count=doc.page_count,
        status=doc.status,
        failure_reason=doc.failure_reason,
        uploaded_at=doc.uploaded_at,
    )


@router.post("", response_model=list[UploadResultOut])
def upload_documents(
    request: Request,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> list[UploadResultOut]:
    """Nhận nhiều tệp; mỗi tệp một kết quả. Tệp hợp lệ ở trạng thái `processing`."""
    runtime = get_runtime(request)
    incoming = [service.IncomingFile(f.filename or "", f.file) for f in files]
    results = service.upload(db, runtime.file_store, runtime.settings, user, incoming)
    return [UploadResultOut(**r.__dict__) for r in results]


@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db, scope="function"), user: CurrentUser = Depends(bd_only)
) -> list[DocumentOut]:
    return [to_out(d) for d in service.list_documents(db, user)]


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> DocumentOut:
    return to_out(service.get_document(db, user, document_id))


@router.post("/{document_id}/retry", response_model=DocumentOut)
def retry_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> DocumentOut:
    return to_out(service.retry(db, user, document_id))


@router.delete("/{document_id}", status_code=202)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(require_role(ROLE_BD, ROLE_SECURITY_ADMIN)),
) -> JSONResponse:
    doc = service.delete_document(db, user, document_id)
    return JSONResponse(status_code=202, content={"id": str(doc.id), "status": doc.status})
