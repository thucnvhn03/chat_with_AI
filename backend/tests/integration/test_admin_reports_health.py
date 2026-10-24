"""T3-04 (kiểm toán), T4-02 (báo cáo sử dụng), T4-03 (đánh giá trong báo cáo), T4-04 (health)."""

import uuid
from datetime import UTC, date, datetime, timedelta  # noqa: F401

import pytest
from sqlalchemy import update

from app.db import transaction
from app.modules.audit import service as audit_service
from app.modules.audit.models import AuditRecord
from app.modules.jobs import queue
from app.modules.jobs.models import Job
from app.modules.usage.models import UsageEvent
from app.modules.usage.reports import week_start, weekly_usage
from tests.conftest import create_user, login
from tests.integration.helpers import ask, bd_client, ready_document

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------- kiểm toán (T3-04, AC-023)


@pytest.fixture
def admin(make_client, runtime):  # type: ignore[no-untyped-def]
    create_user(runtime, "admin", "security_admin")
    client = make_client()
    login(client, "admin")
    return client


def test_audit_lists_one_record_per_question_without_content(
    make_client, runtime, worker, admin
) -> None:  # type: ignore[no-untyped-def]
    an = bd_client(make_client, runtime, "an")
    doc = ready_document(an, worker, "HopDong.pdf", ["Thời hạn thanh toán là 30 ngày."])
    question = "Thời hạn thanh toán là bao nhiêu ngày?"
    ask(an, question)
    ask(an, question)

    page = admin.get("/api/v1/admin/audit").json()
    assert len(page["items"]) == 2 and page["next_cursor"] is None
    item = page["items"][0]
    assert item["user"]["login"] == "an"
    assert item["documents"] == [{"id": doc, "file_name": "HopDong.pdf"}]
    assert question not in str(page) and "30 ngày" not in str(page)


def _count_all(admin, query: str) -> int:  # type: ignore[no-untyped-def]
    total, cursor = 0, None
    while True:
        suffix = f"&cursor={cursor}" if cursor else ""
        page = admin.get(f"/api/v1/admin/audit?{query}{suffix}").json()
        total += len(page["items"])
        cursor = page["next_cursor"]
        if not cursor:
            return total


def test_audit_filters_and_cursor(make_client, runtime, admin) -> None:  # type: ignore[no-untyped-def]
    an_id = create_user(runtime, "an", "bd")
    binh_id = create_user(runtime, "binh", "bd")
    doc = uuid.uuid4()
    with transaction(runtime.sessions) as db:
        for i in range(60):
            audit_service.record(db, an_id if i % 2 else binh_id, [doc] if i < 10 else [])
        db.flush()
        db.execute(
            update(AuditRecord)
            .where(AuditRecord.id <= 5)
            .values(at=datetime.now(UTC) - timedelta(days=10))
        )

    first = admin.get("/api/v1/admin/audit").json()
    assert len(first["items"]) == 50 and first["next_cursor"]
    second = admin.get(f"/api/v1/admin/audit?cursor={first['next_cursor']}").json()
    assert len(second["items"]) == 10 and second["next_cursor"] is None
    ids = [i["id"] for i in first["items"] + second["items"]]
    assert ids == sorted(ids, reverse=True) and len(set(ids)) == 60

    only_an = admin.get("/api/v1/admin/audit?user=an").json()["items"]
    assert len(only_an) == 30 and {i["user"]["login"] for i in only_an} == {"an"}
    by_doc = admin.get(f"/api/v1/admin/audit?document={doc}").json()["items"]
    assert len(by_doc) == 10
    today = datetime.now(UTC).date().isoformat()
    assert _count_all(admin, f"from={today}&to={today}") == 55
    week_ago = (datetime.now(UTC).date() - timedelta(days=7)).isoformat()
    assert _count_all(admin, f"to={week_ago}") == 5
    assert admin.get("/api/v1/admin/audit?document=khong-co-ten-nay").json()["items"] == []


def test_audit_retention_cleanup(runtime) -> None:  # type: ignore[no-untyped-def]
    user = uuid.uuid4()
    with transaction(runtime.sessions) as db:
        audit_service.record(db, user, [])
        db.add(
            AuditRecord(user_id=user, document_ids=[], at=datetime.now(UTC) - timedelta(days=400))
        )
    with transaction(runtime.sessions) as db:
        removed = audit_service.cleanup(db, runtime.settings.audit_retention_days)
    assert removed == 1
    with runtime.sessions() as db:
        assert audit_service.count_for_user(db, user) == 1


# ---------------------------------------------------------------- báo cáo sử dụng (T4-02, T4-03)


def _event(db, user: uuid.UUID, kind: str, at: datetime) -> None:  # type: ignore[no-untyped-def]
    db.add(UsageEvent(user_id=user, kind=kind, at=at))


def test_weekly_usage_with_seed_data(runtime) -> None:  # type: ignore[no-untyped-def]
    """AC-016, AC-021: dữ liệu hạt giống đã biết → số liệu đúng."""
    today = date(2026, 10, 22)  # thứ Năm
    this_week = week_start(today)
    u1, u2, u3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    def at(week_offset: int, day: int = 1) -> datetime:
        d = this_week - timedelta(weeks=week_offset) + timedelta(days=day)
        return datetime(d.year, d.month, d.day, 10, tzinfo=UTC)

    with transaction(runtime.sessions) as db:
        # Tuần này: 2 người hoạt động, 3 câu hỏi
        _event(db, u1, "session_started", at(0))
        _event(db, u1, "question_submitted", at(0))
        _event(db, u1, "question_submitted", at(0, 2))
        _event(db, u2, "question_submitted", at(0, 2))
        # Tuần trước: 3 người, 1 câu hỏi
        for u in (u1, u2, u3):
            _event(db, u, "session_started", at(1))
        _event(db, u3, "question_submitted", at(1))
        # Ngoài khoảng 4 tuần: không được đếm
        _event(db, u1, "question_submitted", at(6))
        # Sự kiện khác không tính là hoạt động
        _event(db, uuid.uuid4(), "access_denied", at(0))

    with runtime.sessions() as db:
        weeks = weekly_usage(db, 4, today=today)
    assert [w.week_start for w in weeks] == [this_week - timedelta(weeks=i) for i in (3, 2, 1, 0)]
    assert [(w.active_users, w.questions) for w in weeks] == [(0, 0), (0, 0), (3, 1), (2, 3)]
    assert all(w.helpful_ratio is None for w in weeks)


def test_usage_endpoint_includes_helpful_ratio(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    an = bd_client(make_client, runtime, "an")
    ready_document(an, worker, "HopDong.pdf", ["Thời hạn thanh toán là 30 ngày."])
    answers = [ask(an, "Thời hạn thanh toán là bao nhiêu ngày?") for _ in range(3)]
    for result, value in zip(answers, ["helpful", "helpful", "not_helpful"], strict=True):
        an.put(f"/api/v1/messages/{result['message_id']}/feedback", json={"value": value})

    create_user(runtime, "quanly", "manager")
    manager = make_client()
    login(manager, "quanly")
    report = manager.get("/api/v1/reports/usage?weeks=4").json()
    current = report["weeks"][-1]
    assert len(report["weeks"]) == 4
    assert current["active_users"] == 1 and current["questions"] == 3
    assert current["helpful_ratio"] == pytest.approx(2 / 3, abs=1e-3)
    assert current["feedback_count"] == 3
    assert an.get("/api/v1/reports/usage").status_code == 403


# ---------------------------------------------------------------- health (T4-04, AC-022)


def test_ready_ok_when_everything_is_up(client) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert set(response.json()["components"]) == {"database", "storage", "queue"}


def test_ready_fails_when_storage_is_down(client, runtime) -> None:  # type: ignore[no-untyped-def]
    from app.container import default_health_checks

    class DownStore:
        def check(self) -> None:
            raise ConnectionError("kho dừng")

    runtime.health_checks = default_health_checks(runtime.settings, runtime.sessions, DownStore())
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["components"]["storage"]["ok"] is False
    assert response.json()["components"]["database"]["ok"] is True


def test_ready_fails_when_queue_backlog_is_old(client, runtime) -> None:  # type: ignore[no-untyped-def]
    with transaction(runtime.sessions) as db:
        queue.enqueue(db, "ingest", {"document_id": str(uuid.uuid4())})
        db.flush()
        db.execute(update(Job).values(run_after=datetime.now(UTC) - timedelta(hours=2)))
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["components"]["queue"] == {"ok": False, "detail": "queue_backlog"}


def test_ready_fails_when_database_is_down(client, runtime) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import create_engine

    from app.container import default_health_checks
    from app.db import make_session_factory

    dead = make_session_factory(create_engine("postgresql+psycopg://x:y@127.0.0.1:1/z"))
    runtime.health_checks = default_health_checks(runtime.settings, dead, runtime.file_store)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["components"]["database"]["ok"] is False


def test_maintenance_exports_component_health_for_alerting(runtime) -> None:  # type: ignore[no-untyped-def]
    """AC-022: thành phần dừng → số liệu component_up = 0 → luật ComponentUnavailable phát cảnh báo."""
    from app.container import default_health_checks
    from app.observability.metrics import COMPONENT_UP
    from app.worker.maintenance import run_maintenance

    run_maintenance(runtime)
    assert COMPONENT_UP.labels("storage")._value.get() == 1

    class DownStore:
        def check(self) -> None:
            raise ConnectionError("kho dừng")

    runtime.health_checks = default_health_checks(runtime.settings, runtime.sessions, DownStore())
    run_maintenance(runtime)
    assert COMPONENT_UP.labels("storage")._value.get() == 0
    assert COMPONENT_UP.labels("database")._value.get() == 1
