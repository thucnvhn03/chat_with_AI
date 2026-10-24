"""IF-10: báo cáo mức sử dụng theo tuần (US-022, US-023, US-024; S-07). Chỉ `manager`."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import require_role
from app.modules.access.service import ROLE_MANAGER, CurrentUser
from app.modules.usage.reports import weekly_usage

router = APIRouter(prefix="/reports", tags=["reports"])


class WeekOut(BaseModel):
    week: date  # ngày thứ Hai đầu tuần
    active_users: int
    questions: int
    helpful_ratio: float | None
    feedback_count: int


class UsageReport(BaseModel):
    weeks: list[WeekOut]


@router.get("/usage", response_model=UsageReport)
def usage_report(
    weeks: int = Query(4, ge=1, le=52),
    db: Session = Depends(get_db, scope="function"),
    _manager: CurrentUser = Depends(require_role(ROLE_MANAGER)),
) -> UsageReport:
    return UsageReport(
        weeks=[
            WeekOut(
                week=w.week_start,
                active_users=w.active_users,
                questions=w.questions,
                helpful_ratio=w.helpful_ratio,
                feedback_count=w.feedback_count,
            )
            for w in weekly_usage(db, weeks)
        ]
    )
