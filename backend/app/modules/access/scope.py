"""Phạm vi tài liệu của người dùng (US-018, BR-020, ADR-004).

`allowed_document_ids` là nơi DUY NHẤT quyết định người dùng được đọc tài liệu nào. Mọi nơi đọc tài liệu
(danh sách, chi tiết, thử lại, truy xuất, trang nguồn, tệp gốc, xóa, sự kiện mở nguồn) đều đi qua đây.

Cho tới khi OQ-003 chốt phạm vi chia sẻ: tài liệu do chính người dùng tải lên ∪ tài liệu trong
`document_acl` (hiện để trống, chưa có endpoint ghi).
"""

import uuid
from typing import Any

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.modules.access.models import DocumentAcl
from app.modules.documents.models import Document


def allowed_documents_query(user_id: uuid.UUID) -> Select[Any]:
    """Câu truy vấn con trả id tài liệu được phép, để nhúng vào truy vấn khác (lọc ngay trong SQL)."""
    shared = select(DocumentAcl.document_id).where(DocumentAcl.user_id == user_id)
    return select(Document.id).where(or_(Document.owner_id == user_id, Document.id.in_(shared)))


def allowed_document_ids(db: Session, user_id: uuid.UUID) -> set[uuid.UUID]:
    return set(db.scalars(allowed_documents_query(user_id)))


def is_allowed(db: Session, user_id: uuid.UUID, document_id: uuid.UUID) -> bool:
    query = allowed_documents_query(user_id).where(Document.id == document_id)
    return db.scalar(query) is not None
