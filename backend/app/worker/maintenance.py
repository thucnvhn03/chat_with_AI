"""Việc định kỳ của worker: cảnh báo xóa quá hạn (US-007), dọn bản ghi kiểm toán (US-020)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.db import transaction
from app.modules.audit import service as audit
from app.modules.conversation import service as conversations
from app.modules.documents.models import Document
from app.observability.health import run_checks
from app.observability.logging import get_logger
from app.observability.metrics import COMPONENT_UP, DOCUMENTS_DELETING_OVERDUE
from app.runtime import Runtime

log = get_logger("maintenance")


def count_deleting_overdue(runtime: Runtime) -> int:
    cutoff = datetime.now(UTC) - timedelta(hours=runtime.settings.purge_sla_hours)
    with runtime.sessions() as db:
        return int(
            db.scalar(
                select(func.count())
                .select_from(Document)
                .where(Document.status == "deleting", Document.deleted_at < cutoff)
            )
            or 0
        )


def update_component_health(runtime: Runtime) -> None:
    """Chạy các kiểm tra của /health/ready và xuất thành số liệu để hệ thống giám sát cảnh báo (US-021)."""
    _, components = run_checks(runtime.health_checks)
    for name, result in components.items():
        COMPONENT_UP.labels(name).set(1 if result["ok"] else 0)


def run_maintenance(runtime: Runtime) -> None:
    update_component_health(runtime)
    overdue = count_deleting_overdue(runtime)
    DOCUMENTS_DELETING_OVERDUE.set(overdue)
    if overdue:
        # Cảnh báo: log mức error (hệ thống giám sát bắt theo event) + số liệu cho Prometheus
        log.error(
            "alert_documents_deleting_overdue",
            count=overdue,
            sla_hours=runtime.settings.purge_sla_hours,
        )
    with transaction(runtime.sessions) as db:
        removed = audit.cleanup(db, runtime.settings.audit_retention_days)
    if removed:
        log.info("audit_records_expired", removed=removed)
    with transaction(runtime.sessions) as db:
        expired = conversations.cleanup_inactive(db, runtime.settings.message_retention_days)
    if expired:
        log.info("conversations_expired", removed=expired)
