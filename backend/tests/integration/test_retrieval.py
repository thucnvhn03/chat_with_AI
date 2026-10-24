"""T2-02: truy xuất theo quyền — lọc trong truy vấn, chỉ `ready`, đủ top_k khi danh sách được phép nhỏ."""

import uuid

import pytest

from app.db import transaction
from app.modules.access.service import find_or_create_user
from app.modules.documents.models import Document
from app.modules.ingestion.models import Chunk
from app.modules.retrieval.search import search

pytestmark = pytest.mark.integration


def _seed(runtime, owner: uuid.UUID, status: str, texts: list[str]) -> uuid.UUID:  # type: ignore[no-untyped-def]
    doc_id = uuid.uuid4()
    vectors = runtime.embedder.embed(texts)
    with transaction(runtime.sessions) as db:
        db.add(
            Document(
                id=doc_id, owner_id=owner, file_name=f"{doc_id}.pdf", size_bytes=1,
                storage_key="k", status=status, page_count=len(texts),
            )
        )  # fmt: skip
        db.flush()
        for i, (t, v) in enumerate(zip(texts, vectors, strict=True)):
            db.add(
                Chunk(
                    id=uuid.uuid4(), document_id=doc_id, page=i + 1, ordinal=i, text=t, embedding=v
                )
            )
    return doc_id


@pytest.fixture
def owner(runtime) -> uuid.UUID:  # type: ignore[no-untyped-def]
    with transaction(runtime.sessions) as db:
        return find_or_create_user(db, "chu").id


def _search(runtime, query: str, allowed, top_k: int = 8, per_doc: int = 0):  # type: ignore[no-untyped-def]
    with runtime.sessions() as db, db.begin():
        return search(db, runtime.embedder.embed([query])[0], allowed, top_k, per_doc)


def test_chunks_outside_allowed_documents_never_appear(runtime, owner) -> None:  # type: ignore[no-untyped-def]
    mine = _seed(runtime, owner, "ready", ["hợp đồng phân phối an bình thời hạn"])
    other = _seed(runtime, owner, "ready", ["hợp đồng phân phối an bình thời hạn"] * 5)
    results = _search(runtime, "hợp đồng phân phối an bình", {mine})
    assert results and {r.document_id for r in results} == {mine}
    assert other not in {r.document_id for r in results}


@pytest.mark.parametrize("status", ["deleting", "deleted", "processing", "failed"])
def test_only_ready_documents_are_searched(runtime, owner, status: str) -> None:  # type: ignore[no-untyped-def]
    doc = _seed(runtime, owner, status, ["điều khoản bảo mật thông tin"])
    assert _search(runtime, "điều khoản bảo mật", {doc}) == []


def test_small_allowed_set_in_large_store_still_returns_top_k(runtime, owner) -> None:  # type: ignore[no-untyped-def]
    # Kho lớn: 60 tài liệu nhiễu rất giống câu hỏi, tài liệu được phép nằm sâu trong chỉ mục HNSW
    for i in range(60):
        _seed(
            runtime,
            owner,
            "ready",
            [f"báo giá dịch vụ vận chuyển tuyến {i} số {j}" for j in range(10)],
        )
    allowed = _seed(
        runtime, owner, "ready", [f"ghi chú nội bộ mục {j} không liên quan" for j in range(12)]
    )
    results = _search(runtime, "báo giá dịch vụ vận chuyển", {allowed}, top_k=8)
    assert len(results) == 8
    assert {r.document_id for r in results} == {allowed}


def test_max_chunks_per_document(runtime, owner) -> None:  # type: ignore[no-untyped-def]
    a = _seed(runtime, owner, "ready", ["giá gói tiêu chuẩn mười hai triệu"] * 6)
    b = _seed(runtime, owner, "ready", ["giá gói nâng cao"] * 2)
    results = _search(runtime, "giá gói tiêu chuẩn", {a, b}, top_k=8, per_doc=4)
    per_doc = {d: sum(r.document_id == d for r in results) for d in (a, b)}
    assert per_doc[a] == 4 and per_doc[b] == 2
    assert results == sorted(results, key=lambda r: -r.score)


def test_empty_allowed_set(runtime) -> None:  # type: ignore[no-untyped-def]
    assert _search(runtime, "bất kỳ", set()) == []
