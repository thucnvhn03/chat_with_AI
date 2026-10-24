"""Kiểm tra sức khỏe (US-021). /health/live: tiến trình còn sống. /health/ready: các thành phần phụ thuộc."""

from collections.abc import Callable
from dataclasses import dataclass

from app.observability.logging import get_logger

log = get_logger("health")


@dataclass
class CheckResult:
    ok: bool
    detail: str = ""


HealthCheck = Callable[[], CheckResult]


def run_checks(checks: dict[str, HealthCheck]) -> tuple[bool, dict[str, dict[str, object]]]:
    results: dict[str, dict[str, object]] = {}
    all_ok = True
    for name, check in checks.items():
        try:
            result = check()
        except Exception as exc:  # một thành phần lỗi không được làm hỏng cả báo cáo
            log.warning("health_check_failed", component=name, error_type=type(exc).__name__)
            result = CheckResult(False, "unavailable")
        all_ok = all_ok and result.ok
        results[name] = {"ok": result.ok, **({"detail": result.detail} if result.detail else {})}
    return all_ok, results
