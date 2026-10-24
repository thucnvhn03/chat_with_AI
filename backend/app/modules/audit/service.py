"""Bản ghi kiểm toán (M-11, US-020, BR-023).

Mỗi câu hỏi sinh đúng một bản ghi: người hỏi, danh sách tài liệu được phép truy cập lúc hỏi, thời điểm.
KHÔNG lưu nội dung câu hỏi. Bản ghi quá AUDIT_RETENTION_DAYS (OQ-012) bị dọn định kỳ.
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.access.models import User
from app.modules.audit.models import AuditRecord
from app.modules.documents.models import Document


def record(db: Session, user_id: uuid.UUID, document_ids: list[uuid.UUID]) -> None:
    db.add(AuditRecord(user_id=user_id, document_ids=sorted(document_ids), at=datetime.now(UTC)))


@dataclass(frozen=True)
class AuditDocument:
    id: uuid.UUID
    file_name: str | None  # None khi tài liệu đã bị xóa vĩnh viễn và không còn tên


@dataclass(frozen=True)
class AuditItem:
    id: int
    at: datetime
    user_id: uuid.UUID
    user_login: str | None
    documents: list[AuditDocument]


def query(
    db: Session,
    date_from: datetime | None,
    date_to: datetime | None,
    user: str | None,
    document: str | None,
    cursor: int | None,
    limit: int,
) -> tuple[list[AuditItem], int | None]:
    """Lọc theo khoảng thời gian, người dùng (login), tài liệu (id hoặc một phần tên); con trỏ = id."""
    stmt = select(AuditRecord).order_by(AuditRecord.id.desc()).limit(limit + 1)
    if date_from is not None:
        stmt = stmt.where(AuditRecord.at >= date_from)
    if date_to is not None:
        stmt = stmt.where(AuditRecord.at < date_to)
    if cursor is not None:
        stmt = stmt.where(AuditRecord.id < cursor)
    if user:
        stmt = stmt.where(
            AuditRecord.user_id.in_(select(User.id).where(User.login.ilike(f"%{user.strip()}%")))
        )
    if document:
        try:
            doc_ids = [uuid.UUID(document.strip())]
        except ValueError:
            doc_ids = list(
                db.scalars(
                    select(Document.id).where(Document.file_name.ilike(f"%{document.strip()}%"))
                )
            )
        if not doc_ids:
            return [], None
        stmt = stmt.where(AuditRecord.document_ids.overlap(doc_ids))

    rows = list(db.scalars(stmt))
    next_cursor = rows[limit - 1].id if len(rows) > limit else None
    rows = rows[:limit]

    user_ids = {r.user_id for r in rows}
    logins = dict(db.execute(select(User.id, User.login).where(User.id.in_(user_ids))).all())
    all_doc_ids = {d for r in rows for d in r.document_ids}
    names = dict(
        db.execute(
            select(Document.id, Document.file_name).where(Document.id.in_(all_doc_ids))
        ).all()
    )
    items = [
        AuditItem(
            id=r.id,
            at=r.at,
            user_id=r.user_id,
            user_login=logins.get(r.user_id),
            documents=[AuditDocument(d, names.get(d)) for d in r.document_ids],
        )
        for r in rows
    ]
    return items, next_cursor


def cleanup(db: Session, retention_days: int) -> int:
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    result = db.execute(delete(AuditRecord).where(AuditRecord.at < cutoff))
    return int(getattr(result, "rowcount", 0) or 0)


def count_for_user(db: Session, user_id: uuid.UUID) -> int:
    return int(
        db.scalar(
            select(func.count()).select_from(AuditRecord).where(AuditRecord.user_id == user_id)
        )
        or 0
    )
