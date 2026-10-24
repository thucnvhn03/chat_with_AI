"""Sự kiện sử dụng (PRD 5.2, implement_plan.md mục 12). Chỉ ghi người dùng, loại sự kiện, thời điểm.

Thuộc tính đi kèm (nhóm lý do lỗi, số nguồn, độ trễ...) chỉ ghi ra log có cấu trúc, không bao giờ kèm
nội dung tài liệu hay câu hỏi.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.modules.usage.models import UsageEvent
from app.observability.logging import get_logger

log = get_logger("usage.events")

SESSION_STARTED = "session_started"
QUESTION_SUBMITTED = "question_submitted"
ANSWER_RETURNED = "answer_returned"
DOCUMENT_UPLOAD_STARTED = "document_upload_started"
DOCUMENT_UPLOAD_SUCCEEDED = "document_upload_succeeded"
DOCUMENT_UPLOAD_FAILED = "document_upload_failed"
DOCUMENT_DELETED = "document_deleted"
SOURCE_OPENED = "source_opened"
ANSWER_FEEDBACK_SUBMITTED = "answer_feedback_submitted"
ACCESS_DENIED = "access_denied"


def record(db: Session, user_id: uuid.UUID, kind: str, **attributes: Any) -> None:
    db.add(UsageEvent(user_id=user_id, kind=kind, at=datetime.now(UTC)))
    log.info("analytics_event", kind=kind, user_id=str(user_id), **attributes)


def record_session_started_once_per_day(db: Session, user_id: uuid.UUID) -> None:
    """`session_started` khi đăng nhập hoặc khi phiên hoạt động lần đầu trong ngày (US-022)."""
    start_of_day = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    already = db.scalar(
        select(
            exists().where(
                UsageEvent.user_id == user_id,
                UsageEvent.kind == SESSION_STARTED,
                UsageEvent.at >= start_of_day,
            )
        )
    )
    if not already:
        record(db, user_id, SESSION_STARTED)
