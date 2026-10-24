"""T0-04: định dạng lỗi chung, log không chứa nội dung, health, ID yêu cầu."""

import json
import logging
import sys
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.config import get_settings
from app.main import create_app
from app.observability.health import CheckResult
from app.observability.logging import configure_logging, get_logger, redact_content


def _fake_runtime(checks: dict[str, Any] | None = None) -> Any:
    return SimpleNamespace(
        settings=get_settings(),
        engine=SimpleNamespace(dispose=lambda: None),
        health_checks=checks or {},
    )


class Echo(BaseModel):
    question: str


def _app_with_routes(checks: dict[str, Any] | None = None):  # type: ignore[no-untyped-def]
    app = create_app(lambda: _fake_runtime(checks))
    router = APIRouter()

    @router.get("/boom")
    def boom() -> None:
        raise RuntimeError("chi tiết nội bộ: /srv/app/secret.py dòng 42")

    @router.post("/echo")
    def echo(body: Echo) -> dict[str, int]:
        get_logger("test").info("received", question=body.question, size=len(body.question))
        return {"size": len(body.question)}

    app.include_router(router)
    return app


def test_unhandled_error_has_standard_format_without_stack_trace() -> None:
    with TestClient(_app_with_routes(), raise_server_exceptions=False) as client:
        response = client.get("/boom")
    assert response.status_code == 500
    body = response.json()
    assert body == {"error": {"code": "internal_error", "message": body["error"]["message"]}}
    text = response.text
    assert "Traceback" not in text and "secret.py" not in text and "RuntimeError" not in text


def test_not_found_uses_error_format() -> None:
    with TestClient(_app_with_routes()) as client:
        response = client.get("/khong-ton-tai")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_validation_error_does_not_echo_input() -> None:
    with TestClient(_app_with_routes()) as client:
        response = client.post("/echo", json={"question": 12345, "extra": "BI-MAT-XYZ"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_input"
    assert "BI-MAT-XYZ" not in response.text


def test_request_log_does_not_contain_question_value(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")
    # Handler giữ stream lúc cấu hình; trỏ lại vào stdout đang được capsys bắt
    logging.getLogger().handlers[0].setStream(sys.stdout)  # type: ignore[attr-defined]
    logging.getLogger().setLevel(logging.INFO)
    marker = "CANARY-7f3a-cau-hoi-bi-mat"
    with TestClient(_app_with_routes()) as client:
        response = client.post("/echo", json={"question": marker})
    assert response.status_code == 200
    out = capsys.readouterr().out
    assert marker not in out
    # Log vẫn được ghi (dạng JSON), chỉ trường nội dung bị loại
    events = [json.loads(line) for line in out.splitlines() if line.startswith("{")]
    received = [e for e in events if e.get("event") == "received"]
    assert received and "question" not in received[0] and received[0]["size"] == len(marker)
    assert any(e.get("event") == "http_request" and e.get("route") == "/echo" for e in events)


def test_redact_processor_strips_nested_content_keys() -> None:
    event = {
        "event": "x",
        "text": "nội dung",
        "meta": {"content": "bí mật", "ok": 1, "items": [{"body": "b", "n": 2}]},
    }
    result = redact_content(None, "info", event)
    assert result == {"event": "x", "meta": {"ok": 1, "items": [{"n": 2}]}}


def test_health_live_and_ready() -> None:
    checks = {"database": lambda: CheckResult(True)}
    with TestClient(_app_with_routes(checks)) as client:
        assert client.get("/health/live").json() == {"status": "ok"}
        ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["components"]["database"]["ok"] is True


def test_health_ready_reports_failed_component() -> None:
    def broken() -> CheckResult:
        raise ConnectionError("không kết nối được")

    checks = {"database": lambda: CheckResult(True), "storage": broken}
    with TestClient(_app_with_routes(checks)) as client:
        ready = client.get("/health/ready")
    assert ready.status_code == 503
    body = ready.json()
    assert body["status"] == "unavailable"
    assert body["components"]["storage"] == {"ok": False, "detail": "unavailable"}
    assert "không kết nối" not in ready.text


def test_response_carries_request_id() -> None:
    with TestClient(_app_with_routes()) as client:
        response = client.get("/health/live", headers={"X-Request-ID": "abc123"})
    assert response.headers["X-Request-ID"] == "abc123"


def test_every_threshold_is_configurable() -> None:
    """Ngưỡng ở implement_plan.md mục 10.3 đều là trường cấu hình (không viết cứng)."""
    fields = set(type(get_settings()).model_fields)
    for name in [
        "max_file_bytes",
        "max_docs_per_user",
        "max_question_chars",
        "chunk_tokens",
        "chunk_overlap",
        "top_k",
        "max_chunks_per_doc",
        "min_relevance_score",
        "answer_model",
        "answer_effort",
        "answer_timeout_s",
        "history_turns",
        "embedding_model",
        "embedding_dim",
        "session_idle_hours",
        "purge_sla_hours",
        "audit_retention_days",
        "job_max_attempts",
        "worker_concurrency",
        "poll_interval_s",
    ]:
        assert name in fields, name
