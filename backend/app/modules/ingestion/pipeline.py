"""Bộ xử lý việc `ingest` (implement_plan.md mục 5.1, phần worker; T1-15).

Đọc tệp từ kho → trích xuất theo trang → chunk → embedding theo lô → ghi TOÀN BỘ chunk và đặt
`status='ready'` trong MỘT giao dịch. Không bao giờ có tài liệu `ready` mà thiếu chunk.
Nếu trong lúc xử lý tài liệu đã chuyển sang `deleting` (hoặc trạng thái khác), kết quả bị bỏ.
"""

import time
import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import transaction
from app.modules.documents.models import Document
from app.modules.ingestion.chunking import chunk_pages
from app.modules.ingestion.extract import ExtractionError, extract_pages
from app.modules.ingestion.models import Chunk
from app.modules.usage import events
from app.observability.logging import get_logger
from app.observability.metrics import INGEST_DURATION
from app.runtime import Runtime

log = get_logger("ingestion")


def _lock_processing(db: Session, document_id: uuid.UUID) -> Document | None:
    doc = db.scalar(select(Document).where(Document.id == document_id).with_for_update())
    if doc is None or doc.status != "processing":
        return None
    return doc


def _fail(runtime: Runtime, document_id: uuid.UUID, reason: str) -> None:
    with transaction(runtime.sessions) as db:
        doc = _lock_processing(db, document_id)
        if doc is None:
            return
        doc.status = "failed"
        doc.failure_reason = reason
        events.record(
            db, doc.owner_id, events.DOCUMENT_UPLOAD_FAILED, reason=reason, document_id=str(doc.id)
        )


def ingest_document(runtime: Runtime, payload: dict[str, Any]) -> None:
    settings = runtime.settings
    document_id = uuid.UUID(payload["document_id"])
    started = time.perf_counter()

    with runtime.sessions() as db:
        doc = db.get(Document, document_id)
        if doc is None or doc.status != "processing":
            log.info("ingest_skipped", document_id=str(document_id))
            return
        storage_key = doc.storage_key

    # Lỗi đọc kho (mạng...) là lỗi tạm thời: để ngoại lệ nổi lên, hàng đợi sẽ thử lại.
    data = runtime.file_store.get(storage_key)

    try:
        pages = extract_pages(data, settings.min_text_chars)
    except ExtractionError as exc:
        log.info("ingest_rejected", document_id=str(document_id), reason=exc.reason)
        _fail(runtime, document_id, exc.reason)
        return

    chunks = chunk_pages(
        pages, runtime.embedder.count_tokens, settings.chunk_tokens, settings.chunk_overlap
    )
    if not chunks:
        _fail(runtime, document_id, "no_text")
        return

    vectors: list[list[float]] = []
    for i in range(0, len(chunks), settings.embed_batch):
        batch = chunks[i : i + settings.embed_batch]
        vectors.extend(runtime.embedder.embed([c.text for c in batch]))

    with transaction(runtime.sessions) as db:
        doc = _lock_processing(db, document_id)
        if doc is None:
            log.info("ingest_discarded", document_id=str(document_id))
            return
        # Lần thử trước có thể đã bị ngắt giữa chừng: làm lại từ đầu cho chắc
        db.execute(delete(Chunk).where(Chunk.document_id == document_id))
        db.add_all(
            Chunk(
                id=uuid.uuid4(),
                document_id=document_id,
                page=c.page,
                ordinal=c.ordinal,
                text=c.text,
                embedding=v,
            )
            for c, v in zip(chunks, vectors, strict=True)
        )
        doc.page_count = len(pages)
        doc.status = "ready"
        doc.failure_reason = None
        events.record(
            db, doc.owner_id, events.DOCUMENT_UPLOAD_SUCCEEDED, document_id=str(document_id)
        )

    elapsed = time.perf_counter() - started
    INGEST_DURATION.observe(elapsed)
    log.info(
        "ingest_done",
        document_id=str(document_id),
        pages=len(pages),
        chunks=len(chunks),
        duration_s=round(elapsed, 2),
    )


def mark_ingest_failed(runtime: Runtime, payload: dict[str, Any]) -> None:
    """Hết số lần thử với lỗi tạm thời → `failed` + `internal` (mục 5.1 bước 8)."""
    _fail(runtime, uuid.UUID(payload["document_id"]), "internal")
