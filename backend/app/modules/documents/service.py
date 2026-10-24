"""Tải lên, danh sách, chi tiết, thử lại, xóa tài liệu (M-04; implement_plan.md mục 5.1, 5.4).

Mọi chỗ đọc tài liệu đều lọc theo `allowed_document_ids` (modules/access/scope.py). Tài liệu ngoài phạm
vi trả 404 như thể không tồn tại.
"""

import io
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import BinaryIO

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import AppError, not_found
from app.modules.access.scope import allowed_documents_query
from app.modules.access.service import ROLE_SECURITY_ADMIN, CurrentUser
from app.modules.documents.models import Document
from app.modules.jobs import queue
from app.modules.usage import events
from app.observability.logging import get_logger
from app.ports.storage import FileStore

log = get_logger("documents")

PDF_MAGIC = b"%PDF-"
VISIBLE_STATUSES = ("uploading", "processing", "ready", "failed")
# Mã lỗi chỉ có trong phản hồi tải lên (tệp bị từ chối không được lưu thành bản ghi tài liệu)
LIMIT_REACHED = "too_many_documents"


@dataclass(frozen=True)
class IncomingFile:
    file_name: str
    stream: BinaryIO


@dataclass(frozen=True)
class UploadResult:
    id: uuid.UUID | None
    file_name: str
    status: str
    failure_reason: str | None


def storage_key(owner_id: uuid.UUID, document_id: uuid.UUID) -> str:
    return f"documents/{owner_id}/{document_id}.pdf"


def _read_limited(stream: BinaryIO, limit: int) -> bytes | None:
    """Đọc tối đa limit+1 byte; trả None nếu tệp vượt giới hạn (không đọc hết tệp quá lớn vào bộ nhớ)."""
    data = stream.read(limit + 1)
    return None if len(data) > limit else data


def _count_documents(db: Session, owner_id: uuid.UUID) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(Document)
            .where(Document.owner_id == owner_id, Document.status.in_(VISIBLE_STATUSES))
        )
        or 0
    )


def upload(
    db: Session,
    file_store: FileStore,
    settings: Settings,
    user: CurrentUser,
    files: list[IncomingFile],
) -> list[UploadResult]:
    """Xử lý TỪNG tệp độc lập: một tệp lỗi không làm hỏng các tệp khác (AC-002)."""
    results: list[UploadResult] = []
    existing = _count_documents(db, user.id)
    for incoming in files:
        name = (incoming.file_name or "tai-lieu.pdf")[:255]
        events.record(db, user.id, events.DOCUMENT_UPLOAD_STARTED)

        def reject(reason: str, name: str = name) -> None:
            events.record(db, user.id, events.DOCUMENT_UPLOAD_FAILED, reason=reason)
            results.append(UploadResult(None, name, "failed", reason))

        data = _read_limited(incoming.stream, settings.max_file_bytes)
        if data is None:
            reject("too_large")
            continue
        # Không tin đuôi tệp hay Content-Type: kiểm tra 5 byte đầu
        if not data.startswith(PDF_MAGIC):
            reject("not_pdf")
            continue
        if existing >= settings.max_docs_per_user:
            reject(LIMIT_REACHED)
            continue

        document_id = uuid.uuid4()
        key = storage_key(user.id, document_id)
        try:
            file_store.put(key, io.BytesIO(data))
        except Exception as exc:
            log.error("upload_store_failed", error_type=type(exc).__name__)
            reject("internal")
            continue

        # Bản ghi tài liệu và việc nạp nằm trong CÙNG giao dịch (savepoint của tệp này)
        try:
            with db.begin_nested():
                db.add(
                    Document(
                        id=document_id,
                        owner_id=user.id,
                        file_name=name,
                        size_bytes=len(data),
                        storage_key=key,
                        status="processing",
                    )
                )
                queue.enqueue(db, queue.KIND_INGEST, {"document_id": str(document_id)})
        except Exception as exc:
            log.error("upload_db_failed", error_type=type(exc).__name__)
            file_store.delete(key)
            reject("internal")
            continue
        existing += 1
        results.append(UploadResult(document_id, name, "processing", None))
    return results


def _visible(user_id: uuid.UUID) -> Select[Document]:
    return select(Document).where(
        Document.id.in_(allowed_documents_query(user_id)),
        Document.status.in_(VISIBLE_STATUSES),
    )


def list_documents(db: Session, user: CurrentUser) -> list[Document]:
    """Chỉ tài liệu trong phạm vi người dùng; không trả `deleting`/`deleted` (US-005)."""
    query = _visible(user.id).order_by(Document.uploaded_at.desc(), Document.id)
    return list(db.scalars(query))


def get_document(db: Session, user: CurrentUser, document_id: uuid.UUID) -> Document:
    doc = db.scalar(_visible(user.id).where(Document.id == document_id))
    if doc is None:
        raise not_found("document_not_found", "Không tìm thấy tài liệu.")
    return doc


def retry(db: Session, user: CurrentUser, document_id: uuid.UUID) -> Document:
    doc = db.scalar(_visible(user.id).where(Document.id == document_id).with_for_update())
    if doc is None:
        raise not_found("document_not_found", "Không tìm thấy tài liệu.")
    if doc.status != "failed":
        raise AppError(409, "not_retryable", "Chỉ thử lại được tài liệu đang ở trạng thái lỗi.")
    doc.status = "processing"
    doc.failure_reason = None
    queue.enqueue(db, queue.KIND_INGEST, {"document_id": str(doc.id)})
    return doc


def delete_document(db: Session, user: CurrentUser, document_id: uuid.UUID) -> Document:
    """Bước 1 của mục 5.4: đặt `deleting` + thêm việc `purge` trong một giao dịch.

    Từ lúc này tài liệu không còn được truy xuất (truy vấn chỉ lấy `ready`) — không chờ worker (AC-005).
    Chủ sở hữu xóa được tài liệu của mình; `security_admin` xóa được mọi tài liệu (xử lý sự cố).
    """
    query: Select[Document]
    if user.role == ROLE_SECURITY_ADMIN:
        query = select(Document).where(
            Document.id == document_id, Document.status.in_(VISIBLE_STATUSES)
        )
    else:
        query = _visible(user.id).where(Document.id == document_id)
    doc = db.scalar(query.with_for_update())
    if doc is None:
        raise not_found("document_not_found", "Không tìm thấy tài liệu.")
    if user.role != ROLE_SECURITY_ADMIN and doc.owner_id != user.id:
        raise AppError(403, "not_owner", "Chỉ người tải lên mới xóa được tài liệu này.")
    doc.status = "deleting"
    doc.deleted_at = datetime.now(UTC)
    queue.enqueue(db, queue.KIND_PURGE, {"document_id": str(doc.id)})
    events.record(db, user.id, events.DOCUMENT_DELETED, document_id=str(doc.id))
    return doc
