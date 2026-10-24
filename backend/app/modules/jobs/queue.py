"""Thao tác hàng đợi: thêm việc, lấy việc (FOR UPDATE SKIP LOCKED), hoàn tất, thử lại có giãn cách."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from app.modules.jobs.models import Job

KIND_INGEST = "ingest"
KIND_PURGE = "purge"


@dataclass(frozen=True)
class ClaimedJob:
    id: int
    kind: str
    payload: dict[str, Any]
    attempts: int


def enqueue(db: Session, kind: str, payload: dict[str, Any]) -> None:
    """Thêm việc trong giao dịch của người gọi (cùng giao dịch với thay đổi tài liệu)."""
    db.add(Job(kind=kind, payload=payload))


_CLAIM_SQL = text(
    """
    UPDATE jobs SET status = 'running', attempts = attempts + 1
    WHERE id = (
      SELECT id FROM jobs
      WHERE status = 'queued' AND run_after <= now()
      ORDER BY id
      FOR UPDATE SKIP LOCKED
      LIMIT 1
    )
    RETURNING id, kind, payload, attempts
    """
)


def claim(db: Session) -> ClaimedJob | None:
    """Lấy một việc sẵn sàng. Hai worker không bao giờ lấy cùng một việc (SKIP LOCKED)."""
    row = db.execute(_CLAIM_SQL).first()
    if row is None:
        return None
    return ClaimedJob(id=row.id, kind=row.kind, payload=row.payload, attempts=row.attempts)


def mark_done(db: Session, job_id: int) -> None:
    db.execute(update(Job).where(Job.id == job_id).values(status="done", last_error=None))


def retry_or_fail(
    db: Session, job: ClaimedJob, error: str, max_attempts: int, base_delay_s: float
) -> bool:
    """Lỗi tạm thời: xếp lại với thời gian chờ tăng dần. Trả True nếu đã hết lượt (việc → failed)."""
    if job.attempts >= max_attempts:
        db.execute(
            update(Job).where(Job.id == job.id).values(status="failed", last_error=error[:500])
        )
        return True
    delay = timedelta(seconds=base_delay_s * (2 ** (job.attempts - 1)))
    db.execute(
        update(Job)
        .where(Job.id == job.id)
        .values(status="queued", run_after=datetime.now(UTC) + delay, last_error=error[:500])
    )
    return False


def queue_depth(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(Job.kind, func.count()).where(Job.status == "queued").group_by(Job.kind)
    ).all()
    return {kind: int(count) for kind, count in rows}


def oldest_queued_age_s(db: Session) -> float:
    oldest = db.scalar(select(func.min(Job.run_after)).where(Job.status == "queued"))
    if oldest is None:
        return 0.0
    return max(0.0, (datetime.now(UTC) - oldest).total_seconds())
