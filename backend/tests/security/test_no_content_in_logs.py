"""T4-05 (implement_plan.md mục 9.3, ADR-009): log, sự kiện phân tích, bản ghi kiểm toán không chứa
nội dung tài liệu hay câu hỏi.

Chạy trọn luồng tải lên → hỏi đáp (có nguồn và không tìm thấy) → mở nguồn → đánh giá → xóa → xóa vĩnh
viễn với chuỗi đánh dấu duy nhất trong tài liệu và câu hỏi; gom toàn bộ log và các bảng sự kiện/kiểm toán;
khẳng định chuỗi đánh dấu không xuất hiện.
"""

import io
import json
import logging
import uuid

import pytest
from sqlalchemy import text

from app.observability.logging import configure_logging
from tests.integration.helpers import ask, bd_client, ready_document

pytestmark = pytest.mark.integration


def test_canary_never_reaches_logs_events_or_audit(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    canary_doc = f"CANARY-DOC-{uuid.uuid4().hex[:8]}"
    canary_question = f"CANARY-Q-{uuid.uuid4().hex[:8]}"

    configure_logging("DEBUG")
    root = logging.getLogger()
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(root.handlers[0].formatter)
    root.addHandler(handler)
    previous_level = root.level
    root.setLevel(logging.DEBUG)
    try:
        client = bd_client(make_client, runtime, "an")
        doc = ready_document(
            client,
            worker,
            "HoSo.pdf",
            [f"Mã bí mật của hồ sơ là {canary_doc} và chỉ dùng nội bộ."],
        )
        answer = ask(client, f"Mã bí mật của hồ sơ là gì? {canary_question}")
        assert not answer["not_found"]
        assert canary_doc in answer["answer"]  # nội dung đi tới người dùng là đúng
        ask(client, f"Thủ đô nước Úc? {canary_question}", answer["conversation_id"])
        client.get(f"/api/v1/documents/{doc}/pages/1")
        client.post("/api/v1/events/source-opened", json={"document_id": doc, "page": 1})
        client.put(f"/api/v1/messages/{answer['message_id']}/feedback", json={"value": "helpful"})
        bad = client.post(
            f"/api/v1/conversations/{answer['conversation_id']}/messages",
            json={"question": canary_question * 400},
        )
        assert bad.status_code == 400 and canary_question not in bad.text
        client.delete(f"/api/v1/documents/{doc}")
        worker.drain()
    finally:
        root.removeHandler(handler)
        root.setLevel(previous_level)

    logs = buffer.getvalue()
    assert "http_request" in logs  # log thật sự được thu
    assert canary_doc not in logs
    assert canary_question not in logs

    with runtime.engine.connect() as conn:
        for table in ("usage_events", "audit_records", "jobs"):
            rows = conn.execute(text(f"SELECT * FROM {table}")).mappings().all()  # noqa: S608
            dump = json.dumps([dict(r) for r in rows], default=str)
            assert rows, table
            assert canary_doc not in dump, table
            assert canary_question not in dump, table
