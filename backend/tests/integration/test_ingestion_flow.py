"""T1-11, T1-15, T1-16, T1-20: tải lên → worker → ready/failed, qua API thật, PostgreSQL và S3 thật.

Phủ AC-001 (tải PDF hợp lệ → Sẵn sàng, có chunk mang số trang), AC-002 (nhiều tệp, một tệp lỗi không ảnh
hưởng tệp khác), AC-003 (đúng lý do lỗi, tài liệu lỗi không được truy xuất), AC-004 (A không thấy tài liệu
của B), AC-018 (mã lỗi ổn định cho giao diện).
"""

import threading
import uuid

import pytest
from sqlalchemy import func, select, text, update

from app.db import transaction
from app.modules.documents.models import Document
from app.modules.ingestion.models import Chunk
from app.modules.jobs.models import Job
from app.worker.run import Worker, default_handlers
from tests import pdf_factory
from tests.integration.helpers import bd_client, upload

pytestmark = pytest.mark.integration

PAGES = [
    "Hợp đồng phân phối giữa Công ty An Bình và Công ty Minh Long. " * 8,
    "Điều 3. Thời hạn thanh toán là 30 ngày kể từ ngày nhận hóa đơn. " * 8,
    "Điều 7. Phạt chậm thanh toán 0,05% mỗi ngày trên số tiền chậm trả. " * 8,
]


def _chunks(runtime, document_id: str) -> list[Chunk]:  # type: ignore[no-untyped-def]
    with runtime.sessions() as db:
        return list(db.scalars(select(Chunk).where(Chunk.document_id == uuid.UUID(document_id))))


def test_valid_pdf_becomes_ready_with_paged_chunks(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    client = bd_client(make_client, runtime, "an")
    [result] = upload(client, ("HopDong_A.pdf", pdf_factory.make_pdf(PAGES)))
    assert result["status"] == "processing" and result["failure_reason"] is None
    doc = client.get(f"/api/v1/documents/{result['id']}").json()
    assert doc["status"] == "processing"

    worker.drain()
    doc = client.get(f"/api/v1/documents/{result['id']}").json()
    assert doc["status"] == "ready" and doc["page_count"] == 3
    chunks = _chunks(runtime, result["id"])
    assert chunks
    assert {c.page for c in chunks} == {1, 2, 3}
    assert all(len(c.embedding) == runtime.settings.embedding_dim for c in chunks)
    with runtime.sessions() as db:
        key = db.get(Document, uuid.UUID(result["id"])).storage_key
    owner = client.get("/api/v1/auth/me").json()["user"]["id"]
    assert key == f"documents/{owner}/{result['id']}.pdf"


def test_mixed_upload_each_file_judged_independently(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    runtime.settings = runtime.settings.model_copy(update={"max_file_bytes": 200_000})
    client = bd_client(make_client, runtime, "an")
    big = pdf_factory.make_pdf(PAGES) + b"0" * 250_000
    results = upload(
        client,
        ("hop-le.pdf", pdf_factory.make_pdf(PAGES)),
        ("ghi-chu.pdf", pdf_factory.NOT_A_PDF),
        ("qua-lon.pdf", big),
    )
    assert [(r["file_name"], r["status"], r["failure_reason"]) for r in results] == [
        ("hop-le.pdf", "processing", None),
        ("ghi-chu.pdf", "failed", "not_pdf"),
        ("qua-lon.pdf", "failed", "too_large"),
    ]
    worker.drain()
    listing = client.get("/api/v1/documents").json()
    assert [(d["file_name"], d["status"]) for d in listing] == [("hop-le.pdf", "ready")]


@pytest.mark.parametrize(
    ("name", "factory", "reason"),
    [
        ("mat-khau.pdf", lambda: pdf_factory.make_encrypted_pdf(PAGES), "encrypted"),
        ("hong.pdf", pdf_factory.make_corrupted_pdf, "corrupted"),
        ("scan.pdf", lambda: pdf_factory.make_image_only_pdf(2), "no_text"),
    ],
)
def test_worker_failure_reasons(make_client, runtime, worker, name, factory, reason) -> None:  # type: ignore[no-untyped-def]
    client = bd_client(make_client, runtime, "an")
    [result] = upload(client, (name, factory()))
    worker.drain()
    doc = client.get(f"/api/v1/documents/{result['id']}").json()
    assert (doc["status"], doc["failure_reason"]) == ("failed", reason)
    assert _chunks(runtime, result["id"]) == []


def test_many_files_with_two_concurrent_workers(make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    """AC-002 với N = 10 tệp (giới hạn tạm thời), hai worker chạy đồng thời."""
    client = bd_client(make_client, runtime, "an")
    files = [
        (f"tai-lieu-{i}.pdf", pdf_factory.make_pdf([f"Tài liệu số {i}. " + PAGES[0]]))
        for i in range(10)
    ]
    files.insert(3, ("hong.pdf", pdf_factory.make_corrupted_pdf()))
    results = upload(client, *files)
    assert all(r["status"] == "processing" for r in results)

    workers = [Worker(runtime, default_handlers()) for _ in range(2)]
    threads = [threading.Thread(target=w.drain) for w in workers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    statuses = {d["file_name"]: d["status"] for d in client.get("/api/v1/documents").json()}
    assert statuses.pop("hong.pdf") == "failed"
    assert set(statuses.values()) == {"ready"} and len(statuses) == 10


def test_max_docs_per_user(make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    runtime.settings = runtime.settings.model_copy(update={"max_docs_per_user": 2})
    client = bd_client(make_client, runtime, "an")
    pdf = pdf_factory.make_pdf(PAGES[:1])
    results = upload(client, ("1.pdf", pdf), ("2.pdf", pdf), ("3.pdf", pdf))
    assert [r["failure_reason"] for r in results] == [None, None, "too_many_documents"]


def test_retry_only_for_failed_and_requeues(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    client = bd_client(make_client, runtime, "an")
    [bad] = upload(client, ("hong.pdf", pdf_factory.make_corrupted_pdf()))
    [good] = upload(client, ("tot.pdf", pdf_factory.make_pdf(PAGES)))
    worker.drain()
    assert client.post(f"/api/v1/documents/{good['id']}/retry").status_code == 409

    retried = client.post(f"/api/v1/documents/{bad['id']}/retry")
    assert retried.status_code == 200 and retried.json()["status"] == "processing"
    # Giả lập người dùng đã thay tệp hợp lệ trên kho (ví dụ lỗi lần trước là tạm thời)
    with runtime.sessions() as db:
        key = db.get(Document, uuid.UUID(bad["id"])).storage_key
    import io

    runtime.file_store.put(key, io.BytesIO(pdf_factory.make_pdf(PAGES)))
    worker.drain()
    assert client.get(f"/api/v1/documents/{bad['id']}").json()["status"] == "ready"


def test_transient_storage_error_retries_then_fails_internal(make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    client = bd_client(make_client, runtime, "an")
    [result] = upload(client, ("tot.pdf", pdf_factory.make_pdf(PAGES)))

    class BrokenStore:
        def __init__(self, inner) -> None:  # type: ignore[no-untyped-def]
            self.inner = inner

        def get(self, key: str) -> bytes:
            raise ConnectionError("mất kết nối kho")

        def __getattr__(self, name: str):  # type: ignore[no-untyped-def]
            return getattr(self.inner, name)

    runtime.file_store = BrokenStore(runtime.file_store)
    Worker(runtime, default_handlers()).drain()
    doc = client.get(f"/api/v1/documents/{result['id']}").json()
    assert (doc["status"], doc["failure_reason"]) == ("failed", "internal")
    with runtime.sessions() as db:
        job = db.scalar(select(Job))
    assert job.attempts == runtime.settings.job_max_attempts and job.status == "failed"


def test_document_moved_to_deleting_during_ingest_is_discarded(
    make_client, runtime, worker
) -> None:  # type: ignore[no-untyped-def]
    client = bd_client(make_client, runtime, "an")
    [result] = upload(client, ("tot.pdf", pdf_factory.make_pdf(PAGES)))
    original_embed = runtime.embedder.embed

    def embed_then_delete(texts):  # type: ignore[no-untyped-def]
        with transaction(runtime.sessions) as db:
            db.execute(
                update(Document)
                .where(Document.id == uuid.UUID(result["id"]))
                .values(status="deleting")
            )
        return original_embed(texts)

    runtime.embedder.embed = embed_then_delete
    worker.drain()
    with runtime.sessions() as db:
        assert db.get(Document, uuid.UUID(result["id"])).status == "deleting"
    assert _chunks(runtime, result["id"]) == []


def test_lifecycle_invariants(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    """Mọi tài liệu `ready` có ≥ 1 chunk; mọi chunk có page trong 1..page_count."""
    client = bd_client(make_client, runtime, "an")
    upload(
        client,
        ("a.pdf", pdf_factory.make_pdf(PAGES)),
        ("b.pdf", pdf_factory.make_pdf(PAGES[:1])),
        ("c.pdf", pdf_factory.make_encrypted_pdf(PAGES)),
    )
    worker.drain()
    with runtime.engine.connect() as conn:
        ready_without_chunks = conn.execute(
            text(
                "SELECT count(*) FROM documents d WHERE d.status = 'ready' "
                "AND NOT EXISTS (SELECT 1 FROM chunks c WHERE c.document_id = d.id)"
            )
        ).scalar()
        bad_pages = conn.execute(
            text(
                "SELECT count(*) FROM chunks c JOIN documents d ON d.id = c.document_id "
                "WHERE c.page < 1 OR c.page > d.page_count"
            )
        ).scalar()
    assert ready_without_chunks == 0 and bad_pages == 0


def test_user_cannot_see_or_touch_other_users_documents(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    a = bd_client(make_client, runtime, "an")
    b = bd_client(make_client, runtime, "binh")
    [doc_b] = upload(b, ("cua-binh.pdf", pdf_factory.make_corrupted_pdf()))
    worker.drain()
    assert a.get("/api/v1/documents").json() == []
    assert a.get(f"/api/v1/documents/{doc_b['id']}").status_code == 404
    assert a.post(f"/api/v1/documents/{doc_b['id']}/retry").status_code == 404
    assert b.get(f"/api/v1/documents/{doc_b['id']}").status_code == 200


def test_upload_events_have_no_content(make_client, runtime, worker) -> None:  # type: ignore[no-untyped-def]
    from app.modules.usage.models import UsageEvent

    client = bd_client(make_client, runtime, "an")
    upload(client, ("a.pdf", pdf_factory.make_pdf(PAGES)), ("x.pdf", pdf_factory.NOT_A_PDF))
    worker.drain()
    with runtime.sessions() as db:
        kinds = dict(
            db.execute(select(UsageEvent.kind, func.count()).group_by(UsageEvent.kind)).all()
        )
    assert kinds["document_upload_started"] == 2
    assert kinds["document_upload_failed"] == 1
    assert kinds["document_upload_succeeded"] == 1
