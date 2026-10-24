"""Báo cáo mức sử dụng theo tuần (US-022, US-023, US-024) và ghi đánh giá câu trả lời.

Tuần tính theo lịch ISO (bắt đầu thứ Hai, giờ UTC). Người dùng hoạt động = số người khác nhau có ít nhất
một `session_started` hoặc `question_submitted` trong tuần. Tỷ lệ hữu ích = số đánh giá "hữu ích" ÷ tổng
số đánh giá trong tuần (None khi chưa có đánh giá).
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.usage import events
from app.modules.usage.models import Feedback, UsageEvent

FEEDBACK_VALUES = ("helpful", "not_helpful")


@dataclass(frozen=True)
class WeekStats:
    week_start: date
    active_users: int
    questions: int
    helpful_ratio: float | None
    feedback_count: int


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def weekly_usage(db: Session, weeks: int, today: date | None = None) -> list[WeekStats]:
    today = today or datetime.now(UTC).date()
    first = week_start(today) - timedelta(weeks=weeks - 1)
    since = datetime(first.year, first.month, first.day, tzinfo=UTC)
    week_expr = func.date_trunc("week", func.timezone("UTC", UsageEvent.at))

    active: dict[Any, int] = dict(
        db.execute(
            select(week_expr, func.count(func.distinct(UsageEvent.user_id)))
            .where(
                UsageEvent.at >= since,
                UsageEvent.kind.in_((events.SESSION_STARTED, events.QUESTION_SUBMITTED)),
            )
            .group_by(week_expr)
        ).all()
    )
    questions: dict[Any, int] = dict(
        db.execute(
            select(week_expr, func.count())
            .where(UsageEvent.at >= since, UsageEvent.kind == events.QUESTION_SUBMITTED)
            .group_by(week_expr)
        ).all()
    )
    fb_week = func.date_trunc("week", func.timezone("UTC", Feedback.created_at))
    feedback = {
        w: (int(total), int(helpful or 0))
        for w, total, helpful in db.execute(
            select(
                fb_week,
                func.count(),
                func.count().filter(Feedback.value == "helpful"),
            )
            .where(Feedback.created_at >= since)
            .group_by(fb_week)
        ).all()
    }

    def key(d: date) -> datetime:
        return datetime(d.year, d.month, d.day)

    result: list[WeekStats] = []
    for i in range(weeks):
        start = first + timedelta(weeks=i)
        total, helpful = feedback.get(key(start), (0, 0))
        result.append(
            WeekStats(
                week_start=start,
                active_users=int(active.get(key(start), 0)),
                questions=int(questions.get(key(start), 0)),
                helpful_ratio=round(helpful / total, 4) if total else None,
                feedback_count=total,
            )
        )
    return result


def set_feedback(db: Session, message_id: uuid.UUID, user_id: uuid.UUID, value: str) -> None:
    """Ghi đè được: chọn lại thì cập nhật giá trị và thời điểm."""
    now = datetime.now(UTC)
    stmt = insert(Feedback).values(
        message_id=message_id, user_id=user_id, value=value, created_at=now
    )
    db.execute(
        stmt.on_conflict_do_update(
            index_elements=[Feedback.message_id], set_={"value": value, "created_at": now}
        )
    )
    events.record(db, user_id, events.ANSWER_FEEDBACK_SUBMITTED, value=value)
