"""IF-09: bản ghi kiểm toán (US-020, S-06). Chỉ `security_admin`. Không có nội dung câu hỏi."""

import uuid
from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import require_role
from app.modules.access.service import ROLE_SECURITY_ADMIN, CurrentUser
from app.modules.audit import service

router = APIRouter(prefix="/admin/audit", tags=["admin"])

PAGE_SIZE = 50


class AuditUser(BaseModel):
    id: uuid.UUID
    login: str | None


class AuditDocumentOut(BaseModel):
    id: uuid.UUID
    file_name: str | None


class AuditItemOut(BaseModel):
    id: int
    at: datetime
    user: AuditUser
    documents: list[AuditDocumentOut]


class AuditPage(BaseModel):
    items: list[AuditItemOut]
    next_cursor: str | None


def _start_of(day: date | None) -> datetime | None:
    return datetime.combine(day, time.min, tzinfo=UTC) if day else None


@router.get("", response_model=AuditPage)
def list_audit(
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    user: str | None = Query(None, max_length=200),
    document: str | None = Query(None, max_length=300),
    cursor: int | None = Query(None, ge=1),
    db: Session = Depends(get_db, scope="function"),
    _admin: CurrentUser = Depends(require_role(ROLE_SECURITY_ADMIN)),
) -> AuditPage:
    # `to` tính trọn ngày (đến hết ngày được chọn)
    end = _start_of(date_to + timedelta(days=1)) if date_to else None
    items, next_cursor = service.query(
        db, _start_of(date_from), end, user, document, cursor, PAGE_SIZE
    )
    return AuditPage(
        items=[
            AuditItemOut(
                id=i.id,
                at=i.at,
                user=AuditUser(id=i.user_id, login=i.user_login),
                documents=[AuditDocumentOut(id=d.id, file_name=d.file_name) for d in i.documents],
            )
            for i in items
        ],
        next_cursor=str(next_cursor) if next_cursor is not None else None,
    )
