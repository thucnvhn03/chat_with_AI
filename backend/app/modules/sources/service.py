"""Trang nguồn và tệp gốc (M-09, US-015; implement_plan.md mục 5.5).

Chỉ phục vụ tài liệu trong `allowed_document_ids` và đang `ready`; ngoài ra → 404 (giao diện hiển thị
trạng thái "tài liệu đã bị xóa" của S-03). Văn bản trang lấy bằng cách đọc lại tệp gốc và trích đúng
trang đó bằng mô-đun trích xuất (không lưu bảng trang riêng ở MVP).
"""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import not_found
from app.modules.access.scope import allowed_documents_query
from app.modules.documents.models import Document
from app.modules.ingestion.extract import ExtractionError, extract_page
from app.ports.storage import FileStore


@dataclass(frozen=True)
class PageView:
    page: int
    page_count: int
    text: str
    document_name: str


def _ready_document(db: Session, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
    doc = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.status == "ready",
            Document.id.in_(allowed_documents_query(user_id)),
        )
    )
    if doc is None:
        raise not_found("document_not_found", "Tài liệu không còn hoặc bạn không có quyền xem.")
    return doc


def page_text(
    db: Session, file_store: FileStore, user_id: uuid.UUID, document_id: uuid.UUID, page: int
) -> PageView:
    doc = _ready_document(db, user_id, document_id)
    if page < 1 or (doc.page_count is not None and page > doc.page_count):
        raise not_found("page_not_found", "Trang không tồn tại trong tài liệu.")
    try:
        text, total = extract_page(file_store.get(doc.storage_key), page)
    except IndexError:
        raise not_found("page_not_found", "Trang không tồn tại trong tài liệu.") from None
    except ExtractionError:
        raise not_found("document_not_found", "Không đọc được tài liệu.") from None
    return PageView(page=page, page_count=total, text=text, document_name=doc.file_name)


def original_file(
    db: Session, file_store: FileStore, user_id: uuid.UUID, document_id: uuid.UUID
) -> tuple[str, bytes]:
    doc = _ready_document(db, user_id, document_id)
    return doc.file_name, file_store.get(doc.storage_key)


def ensure_readable(db: Session, user_id: uuid.UUID, document_id: uuid.UUID) -> None:
    _ready_document(db, user_id, document_id)
