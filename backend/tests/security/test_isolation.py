"""T3-07: cô lập quyền giữa người dùng A và B (AC-020, LG-07).

Mỗi người một tài liệu có chuỗi đặc trưng. A không được thấy, hỏi ra, mở trang/tệp, xóa, thử lại tài
liệu của B, không vào được hội thoại hay đánh giá câu trả lời của B. Danh sách route kiểm tra được sinh
tự động: route mới có tham số tài nguyên mà không kiểm quyền sẽ làm kiểm thử đỏ.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.modules.audit.models import AuditRecord
from tests import pdf_factory
from tests.integration.helpers import ask, bd_client, ready_document, upload
from tests.security.routes import add_route, all_routes

pytestmark = pytest.mark.integration

A_TEXT = ["Lịch họp đối tác ALPHA-ORCHID-7781 diễn ra sáng thứ Sáu tại văn phòng Đà Nẵng."]
B_TEXT = ["Ghi chú của Bình: mã khách hàng BRAVO-LOTUS-5523 thuộc khu vực miền Nam."]
RESOURCE_PARAMS = {"document_id", "conversation_id", "message_id"}
BODY = {"question": "BRAVO-LOTUS-5523?", "value": "helpful"}


@pytest.fixture
def two_users(make_client, runtime, worker):  # type: ignore[no-untyped-def]
    a = bd_client(make_client, runtime, "an")
    b = bd_client(make_client, runtime, "binh")
    doc_a = ready_document(a, worker, "an.pdf", A_TEXT)
    doc_b = ready_document(b, worker, "binh.pdf", B_TEXT)
    b_answer = ask(b, "Mã khách hàng BRAVO-LOTUS-5523 thuộc khu vực nào?")
    assert not b_answer["not_found"]
    return a, b, doc_a, doc_b, b_answer


def test_a_cannot_get_b_content_by_asking(two_users) -> None:  # type: ignore[no-untyped-def]
    a, _, _, _, _ = two_users
    result = ask(a, "Mã khách hàng BRAVO-LOTUS-5523 thuộc khu vực nào?")
    assert result["not_found"]
    assert "BRAVO" not in result["answer"]


def test_a_list_does_not_contain_b(two_users) -> None:  # type: ignore[no-untyped-def]
    a, _, doc_a, doc_b, _ = two_users
    ids = {d["id"] for d in a.get("/api/v1/documents").json()}
    assert ids == {doc_a}


def _b_values(two_users) -> dict[str, str]:  # type: ignore[no-untyped-def]
    _, _, _, doc_b, b_answer = two_users
    return {
        "document_id": doc_b,
        "conversation_id": b_answer["conversation_id"],
        "message_id": b_answer["message_id"],
        "page": "1",
    }


def _resource_routes(app) -> list:  # type: ignore[no-untyped-def]
    return [r for r in all_routes(app) if set(r.params) & RESOURCE_PARAMS and not r.is_admin]


def test_every_resource_route_hides_b_resources_from_a(app, two_users) -> None:  # type: ignore[no-untyped-def]
    a = two_users[0]
    values = _b_values(two_users)
    routes = _resource_routes(app)
    checked = {(r.method, r.path) for r in routes}
    # Bảo đảm danh sách bao gồm các route quan trọng của T3-07
    for expected in [
        ("GET", "/api/v1/documents/{document_id}"),
        ("GET", "/api/v1/documents/{document_id}/pages/{page}"),
        ("GET", "/api/v1/documents/{document_id}/file"),
        ("DELETE", "/api/v1/documents/{document_id}"),
        ("POST", "/api/v1/documents/{document_id}/retry"),
        ("POST", "/api/v1/conversations/{conversation_id}/messages"),
        ("GET", "/api/v1/conversations/{conversation_id}/messages"),
        ("PUT", "/api/v1/messages/{message_id}/feedback"),
    ]:
        assert expected in checked
    body = BODY
    for route in routes:
        response = a.request(route.method, route.url(values), json=body)
        assert response.status_code == 404, f"{route.method} {route.path}: {response.status_code}"


def test_source_opened_event_for_b_document_is_rejected(two_users) -> None:  # type: ignore[no-untyped-def]
    a, _, _, doc_b, _ = two_users
    response = a.post("/api/v1/events/source-opened", json={"document_id": doc_b, "page": 1})
    assert response.status_code == 404


def test_b_document_still_intact_after_a_attempts(app, two_users) -> None:  # type: ignore[no-untyped-def]
    a, b, _, doc_b, _ = two_users
    a.delete(f"/api/v1/documents/{doc_b}")
    assert b.get(f"/api/v1/documents/{doc_b}").json()["status"] == "ready"


def test_a_audit_records_never_list_b_documents(two_users, runtime) -> None:  # type: ignore[no-untyped-def]
    import uuid

    a, _, doc_a, doc_b, _ = two_users
    ask(a, "Lịch họp đối tác diễn ra khi nào?")
    a_id = uuid.UUID(a.get("/api/v1/auth/me").json()["user"]["id"])
    with runtime.sessions() as db:
        records = list(db.scalars(select(AuditRecord).where(AuditRecord.user_id == a_id)))
    assert records
    for record in records:
        assert {str(d) for d in record.document_ids} == {doc_a}
        assert doc_b not in {str(d) for d in record.document_ids}


def test_unchecked_resource_route_makes_isolation_fail(app, two_users) -> None:  # type: ignore[no-untyped-def]
    """Thêm cố ý một route đọc tài liệu không kiểm quyền → kiểm tra cô lập phát hiện được."""
    a = two_users[0]

    def leaky(document_id: str) -> dict[str, str]:
        return {"id": document_id}

    add_route(app, "/api/v1/documents/{document_id}/leaky", leaky)
    values = _b_values(two_users)
    leaks = [
        r.path
        for r in _resource_routes(app)
        if a.request(r.method, r.url(values), json=BODY).status_code != 404
    ]
    assert leaks == ["/api/v1/documents/{document_id}/leaky"]


def test_uploads_are_scoped_to_uploader(two_users, worker) -> None:  # type: ignore[no-untyped-def]
    a, b, _, _, _ = two_users
    [new] = upload(a, ("moi.pdf", pdf_factory.make_pdf(["Tài liệu mới của An."])))
    worker.drain()
    assert b.get(f"/api/v1/documents/{new['id']}").status_code == 404
    assert isinstance(b, TestClient)
