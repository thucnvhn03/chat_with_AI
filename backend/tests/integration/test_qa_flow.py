"""T2-05, T2-06, T2-11, T2-12, T3-05, T3-06, T4-03: hỏi đáp qua API thật với fake_llm.

Phủ ở tầng backend: AC-006 (câu trả lời có nguồn), AC-009 (ngoài phạm vi → không tìm thấy), AC-012
(mọi câu trả lời có nội dung có nguồn, đoạn trích nằm trong tài liệu), AC-019 (trang nêu trong nguồn chứa
`cited_text`), AC-008 (hỏi tiếp), AC-017 (đánh giá), AC-023 (một câu hỏi = một bản ghi kiểm toán).
"""

import time

import pytest
from sqlalchemy import func, select

from app.adapters.fake_llm import NOT_FOUND_SENTENCE
from app.modules.audit.models import AuditRecord
from app.modules.usage.models import Feedback, UsageEvent
from tests.integration.helpers import ask, bd_client, ready_document

pytestmark = pytest.mark.integration

CONTRACT = [
    "Hợp đồng phân phối số 12/2026 giữa Công ty An Bình và Công ty Minh Long.",
    "Điều 3. Thời hạn thanh toán là 30 ngày kể từ ngày nhận hóa đơn hợp lệ.",
    "Điều 7. Phạt chậm thanh toán là 0,05% mỗi ngày trên số tiền chậm trả.",
]
QUOTE = [
    "Bảng báo giá dịch vụ lưu kho năm 2026.",
    "Giá gói tiêu chuẩn là 12 triệu đồng mỗi tháng, đã gồm bảo hiểm hàng hóa.",
]


@pytest.fixture
def setup(make_client, runtime, worker):  # type: ignore[no-untyped-def]
    client = bd_client(make_client, runtime, "an")
    contract = ready_document(client, worker, "HopDong_A.pdf", CONTRACT)
    quote = ready_document(client, worker, "BaoGia_B.pdf", QUOTE)
    return client, contract, quote


def _count(runtime, model, *where) -> int:  # type: ignore[no-untyped-def]
    with runtime.sessions() as db:
        return int(db.scalar(select(func.count()).select_from(model).where(*where)) or 0)


def test_answer_has_source_document_and_page(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, contract, _ = setup
    result = ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")
    assert not result["not_found"]
    assert "30 ngày" in result["answer"]
    [citation] = result["citations"]
    assert citation["document_id"] == contract
    assert citation["document_name"] == "HopDong_A.pdf" and citation["page"] == 2
    assert result["latency_ms"] >= 0

    # AC-019: trang được nêu chứa đoạn trích
    page = client.get(f"/api/v1/documents/{contract}/pages/{citation['page']}").json()
    assert citation["cited_text"] in page["text"]
    assert page["page_count"] == 3 and page["document_name"] == "HopDong_A.pdf"


def test_question_across_documents_cites_the_right_one(setup) -> None:  # type: ignore[no-untyped-def]
    client, _, quote = setup
    result = ask(client, "Giá gói tiêu chuẩn lưu kho là bao nhiêu triệu?")
    assert result["citations"][0]["document_id"] == quote
    assert result["citations"][0]["page"] == 2


def test_out_of_scope_question_is_not_found_without_calling_model(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    result = ask(client, "Thủ đô của nước Úc là thành phố nào?")
    assert result["not_found"] and result["citations"] == []
    assert result["answer"] == NOT_FOUND_SENTENCE
    assert runtime.answer_generator.calls == 0


@pytest.mark.parametrize("mode", ["no_citations", "not_found_sentence", "bad_index"])
def test_model_answers_without_valid_citation_become_not_found(setup, runtime, mode: str) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    runtime.answer_generator.mode = mode
    result = ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")
    assert result["not_found"] and result["citations"] == []
    assert runtime.answer_generator.calls == 1


def test_model_refusal_returns_generic_error(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    runtime.answer_generator.mode = "refuse"
    conv = client.post("/api/v1/conversations").json()["id"]
    response = client.post(
        f"/api/v1/conversations/{conv}/messages", json={"question": "Thời hạn thanh toán?"}
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "answer_unavailable"


def test_timeout_returns_504(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    runtime.answer_generator.mode = "timeout"
    conv = client.post("/api/v1/conversations").json()["id"]
    response = client.post(
        f"/api/v1/conversations/{conv}/messages", json={"question": "Thời hạn thanh toán?"}
    )
    assert response.status_code == 504
    assert response.json()["error"]["code"] == "answer_timeout"


def test_slow_generator_hits_answer_timeout(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    runtime.settings = runtime.settings.model_copy(update={"answer_timeout_s": 0.5})
    original = runtime.answer_generator.generate

    def slow(*args, **kwargs):  # type: ignore[no-untyped-def]
        time.sleep(1.5)
        return original(*args, **kwargs)

    runtime.answer_generator.generate = slow
    conv = client.post("/api/v1/conversations").json()["id"]
    started = time.perf_counter()
    response = client.post(
        f"/api/v1/conversations/{conv}/messages", json={"question": "Thời hạn thanh toán?"}
    )
    assert response.status_code == 504
    assert time.perf_counter() - started < 1.4


@pytest.mark.parametrize(
    ("question", "code"), [("   ", "question_empty"), ("x" * 2001, "question_too_long")]
)
def test_question_validation(setup, question: str, code: str) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    conv = client.post("/api/v1/conversations").json()["id"]
    response = client.post(f"/api/v1/conversations/{conv}/messages", json={"question": question})
    assert response.status_code == 400 and response.json()["error"]["code"] == code


def test_each_question_writes_exactly_one_audit_record_without_content(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, contract, quote = setup
    ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")
    ask(client, "Thủ đô của nước Úc?")
    with runtime.sessions() as db:
        records = list(db.scalars(select(AuditRecord)))
    assert len(records) == 2
    assert {str(d) for d in records[0].document_ids} == {contract, quote}
    assert _count(runtime, UsageEvent, UsageEvent.kind == "question_submitted") == 2
    assert _count(runtime, UsageEvent, UsageEvent.kind == "answer_returned") == 2


def test_conversation_belongs_to_owner_only(setup, make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    conv = ask(client, "Thời hạn thanh toán?")["conversation_id"]
    other = bd_client(make_client, runtime, "binh")
    assert other.get(f"/api/v1/conversations/{conv}/messages").status_code == 404
    response = other.post(f"/api/v1/conversations/{conv}/messages", json={"question": "x"})
    assert response.status_code == 404


def test_history_and_follow_up_question(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    first = ask(client, "Hợp đồng có điều khoản phạt chậm thanh toán không?")
    second = ask(client, "Mức đó là bao nhiêu phần trăm mỗi ngày?", first["conversation_id"])
    # Truy vấn truy xuất ghép câu hỏi trước nên câu hỏi tiếp theo dùng đại từ vẫn tìm được Điều 7
    assert not second["not_found"]
    assert second["citations"][0]["page"] == 3
    assert runtime.answer_generator.last_history[0]["role"] == "user"
    assert len(runtime.answer_generator.last_history) == 2

    history = client.get(f"/api/v1/conversations/{first['conversation_id']}/messages").json()
    assert [m["role"] for m in history] == ["user", "assistant", "user", "assistant"]
    assert history[3]["citations"][0]["page"] == 3

    # Hội thoại mới không mang ngữ cảnh cũ
    ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")
    assert runtime.answer_generator.last_history == []


def test_history_is_limited_to_history_turns(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    runtime.settings = runtime.settings.model_copy(update={"history_turns": 1})
    conv = ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")["conversation_id"]
    ask(client, "Phạt chậm thanh toán là bao nhiêu?", conv)
    ask(client, "Hợp đồng phân phối số mấy?", conv)
    assert len(runtime.answer_generator.last_history) == 2


def test_source_page_and_file_access(setup, make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    client, contract, _ = setup
    assert client.get(f"/api/v1/documents/{contract}/pages/4").status_code == 404
    assert client.get(f"/api/v1/documents/{contract}/pages/0").status_code == 404
    pdf = client.get(f"/api/v1/documents/{contract}/file")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-")
    assert pdf.headers["content-type"] == "application/pdf"

    other = bd_client(make_client, runtime, "binh")
    assert other.get(f"/api/v1/documents/{contract}/pages/1").status_code == 404
    assert other.get(f"/api/v1/documents/{contract}/file").status_code == 404


def test_source_opened_event(setup, make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    client, contract, _ = setup
    response = client.post(
        "/api/v1/events/source-opened", json={"document_id": contract, "page": 2}
    )
    assert response.status_code == 204
    assert _count(runtime, UsageEvent, UsageEvent.kind == "source_opened") == 1
    other = bd_client(make_client, runtime, "binh")
    denied = other.post("/api/v1/events/source-opened", json={"document_id": contract, "page": 2})
    assert denied.status_code == 404
    assert _count(runtime, UsageEvent, UsageEvent.kind == "source_opened") == 1


def test_feedback_is_saved_and_can_be_changed(setup, make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = setup
    result = ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")
    url = f"/api/v1/messages/{result['message_id']}/feedback"
    assert client.put(url, json={"value": "helpful"}).status_code == 204
    assert client.put(url, json={"value": "not_helpful"}).status_code == 204
    with runtime.sessions() as db:
        rows = list(db.scalars(select(Feedback)))
    assert [r.value for r in rows] == ["not_helpful"]
    history = client.get(f"/api/v1/conversations/{result['conversation_id']}/messages").json()
    assert history[1]["feedback"] == "not_helpful"
    assert client.put(url, json={"value": "tot"}).status_code == 400

    other = bd_client(make_client, runtime, "binh")
    assert other.put(url, json={"value": "helpful"}).status_code == 404


def test_commit_failure_is_reported_not_swallowed(setup, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Hồi quy: commit phải chạy TRƯỚC khi gửi phản hồi; lỗi commit trả 500 chứ không phải 200."""
    from sqlalchemy.orm import Session

    client, _, _ = setup

    def broken_commit(self) -> None:  # type: ignore[no-untyped-def]
        raise RuntimeError("commit lỗi")

    monkeypatch.setattr(Session, "commit", broken_commit)
    from fastapi.testclient import TestClient

    with TestClient(
        client.app, headers=client.headers, cookies=client.cookies, raise_server_exceptions=False
    ) as c:
        response = c.post("/api/v1/conversations")
    assert response.status_code == 500


def test_inactive_conversations_are_cleaned_up(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    """PQ-004: hội thoại không hoạt động quá MESSAGE_RETENTION_DAYS bị xóa cùng tin nhắn, trích dẫn, đánh giá."""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import update

    from app.db import transaction
    from app.modules.conversation.models import Citation, Conversation, Message
    from app.worker.maintenance import run_maintenance

    client, _, _ = setup
    old = ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")
    client.put(f"/api/v1/messages/{old['message_id']}/feedback", json={"value": "helpful"})
    recent = ask(client, "Phạt chậm thanh toán là bao nhiêu?")
    long_ago = datetime.now(UTC) - timedelta(days=runtime.settings.message_retention_days + 1)
    with transaction(runtime.sessions) as db:
        db.execute(
            update(Conversation)
            .where(Conversation.id == old["conversation_id"])
            .values(created_at=long_ago)
        )
        db.execute(
            update(Message)
            .where(Message.conversation_id == old["conversation_id"])
            .values(created_at=long_ago)
        )

    run_maintenance(runtime)

    assert client.get(f"/api/v1/conversations/{old['conversation_id']}/messages").status_code == 404
    assert client.get(f"/api/v1/conversations/{recent['conversation_id']}/messages").status_code == 200
    assert _count(runtime, Feedback) == 0
    assert _count(runtime, Citation) == 1
    # Bản ghi kiểm toán và sự kiện sử dụng không bị ảnh hưởng
    assert _count(runtime, AuditRecord) == 2


def test_retention_zero_keeps_everything(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    from app.db import transaction
    from app.modules.conversation.service import cleanup_inactive

    client, _, _ = setup
    ask(client, "Thời hạn thanh toán là bao nhiêu ngày?")
    with transaction(runtime.sessions) as db:
        assert cleanup_inactive(db, 0) == 0
