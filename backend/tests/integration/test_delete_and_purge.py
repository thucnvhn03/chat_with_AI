"""T3-01, T3-02: xóa tài liệu (loại khỏi truy vấn NGAY) và worker xóa vĩnh viễn.

Phủ AC-005 (sau khi xóa, câu hỏi chỉ có đáp án trong tài liệu đó → không tìm thấy, kể cả khi worker
chưa chạy) và AC-024 (sau khi worker chạy: không còn chunk, không còn tệp, `purged_at` có giá trị).
"""

import uuid

import pytest
from sqlalchemy import func, select

from app.db import transaction
from app.modules.conversation.models import Citation
from app.modules.documents.models import Document
from app.modules.ingestion.models import Chunk
from app.worker.maintenance import count_deleting_overdue
from app.worker.run import Worker, default_handlers
from tests.conftest import create_user, login
from tests.integration.helpers import ask, bd_client, ready_document

pytestmark = pytest.mark.integration

SECRET_DOC = ["Mật mã dự án Hải Đăng là XANH-LAM-42 dùng cho buổi trình bày với đối tác."]


@pytest.fixture
def setup(make_client, runtime, worker):  # type: ignore[no-untyped-def]
    client = bd_client(make_client, runtime, "an")
    doc = ready_document(client, worker, "DuAn.pdf", SECRET_DOC)
    return client, doc


def _doc(runtime, doc_id: str) -> Document:  # type: ignore[no-untyped-def]
    with runtime.sessions() as db:
        return db.get(Document, uuid.UUID(doc_id))


def test_deleted_document_is_excluded_immediately(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, doc = setup
    assert not ask(client, "Mật mã dự án Hải Đăng là gì?")["not_found"]

    response = client.delete(f"/api/v1/documents/{doc}")
    assert response.status_code == 202 and response.json()["status"] == "deleting"
    # Worker CHƯA chạy: tài liệu vẫn còn chunk nhưng không còn được truy xuất
    with runtime.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Chunk)) > 0
    assert ask(client, "Mật mã dự án Hải Đăng là gì?")["not_found"]
    assert client.get("/api/v1/documents").json() == []
    assert client.get(f"/api/v1/documents/{doc}").status_code == 404
    assert client.get(f"/api/v1/documents/{doc}/pages/1").status_code == 404


def test_purge_removes_chunks_file_and_sets_purged_at(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, doc = setup
    answer = ask(client, "Mật mã dự án Hải Đăng là gì?")
    key = _doc(runtime, doc).storage_key
    client.delete(f"/api/v1/documents/{doc}")
    Worker(runtime, default_handlers()).drain()

    row = _doc(runtime, doc)
    assert row.status == "deleted" and row.purged_at is not None
    with runtime.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Chunk)) == 0
        citation = db.scalar(select(Citation))
    assert not runtime.file_store.exists(key)
    # Đoạn trích nguyên văn đã bị xóa khỏi citation; chỉ còn tên và số trang
    assert citation is not None and citation.cited_text is None
    history = client.get(f"/api/v1/conversations/{answer['conversation_id']}/messages").json()
    assert history[1]["citations"][0]["cited_text"] is None


def test_purge_twice_is_harmless(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    from app.modules.documents.purge import purge_document

    client, doc = setup
    client.delete(f"/api/v1/documents/{doc}")
    purge_document(runtime, {"document_id": doc})
    purge_document(runtime, {"document_id": doc})
    assert _doc(runtime, doc).status == "deleted"


def test_storage_error_midway_is_retried_and_completes(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    client, doc = setup
    key = _doc(runtime, doc).storage_key
    client.delete(f"/api/v1/documents/{doc}")
    real_store = runtime.file_store
    calls = {"n": 0}

    class FlakyStore:
        def delete(self, k: str) -> None:
            calls["n"] += 1
            if calls["n"] == 1:
                raise ConnectionError("kho tệp lỗi")
            real_store.delete(k)

        def __getattr__(self, name: str):  # type: ignore[no-untyped-def]
            return getattr(real_store, name)

    runtime.file_store = FlakyStore()
    Worker(runtime, default_handlers()).drain()
    assert calls["n"] == 2
    assert _doc(runtime, doc).status == "deleted"
    assert not real_store.exists(key)


def test_delete_permissions(setup, make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    _, doc = setup
    other = bd_client(make_client, runtime, "binh")
    assert other.delete(f"/api/v1/documents/{doc}").status_code == 404
    create_user(runtime, "quanly", "manager")
    manager = make_client()
    login(manager, "quanly")
    assert manager.delete(f"/api/v1/documents/{doc}").status_code == 403
    # Quản trị bảo mật xóa được mọi tài liệu (xử lý sự cố)
    create_user(runtime, "admin", "security_admin")
    admin = make_client()
    login(admin, "admin")
    assert admin.delete(f"/api/v1/documents/{doc}").status_code == 202
    assert admin.delete(f"/api/v1/documents/{doc}").status_code == 404


def test_overdue_deleting_documents_are_counted(setup, runtime) -> None:  # type: ignore[no-untyped-def]
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import update

    client, doc = setup
    client.delete(f"/api/v1/documents/{doc}")
    assert count_deleting_overdue(runtime) == 0
    with transaction(runtime.sessions) as db:
        db.execute(update(Document).values(deleted_at=datetime.now(UTC) - timedelta(hours=48)))
    assert count_deleting_overdue(runtime) == 1
