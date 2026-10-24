"""Bộ xử lý việc `purge`: xóa vĩnh viễn tài liệu (US-007, AC-024; implement_plan.md mục 5.4 bước 2).

Thứ tự: xóa chunk → xóa đoạn trích trong citation → xóa tệp trên kho → `status='deleted'`,
`purged_at=now()`. Mỗi bước làm lại được nhiều lần không lỗi; lỗi kho tệp → ngoại lệ → hàng đợi thử lại.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, update

from app.db import transaction
from app.modules.conversation.models import Citation
from app.modules.documents.models import Document
from app.modules.ingestion.models import Chunk
from app.observability.logging import get_logger
from app.runtime import Runtime

log = get_logger("purge")


def purge_document(runtime: Runtime, payload: dict[str, Any]) -> None:
    document_id = uuid.UUID(payload["document_id"])
    with runtime.sessions() as db:
        doc = db.get(Document, document_id)
        if doc is None:
            return
        if doc.status == "deleted":
            log.info("purge_already_done", document_id=str(document_id))
            return
        if doc.status != "deleting":
            # Không xóa tài liệu chưa được yêu cầu xóa (phòng việc bị thêm nhầm)
            log.warning("purge_skipped_wrong_status", document_id=str(document_id))
            return
        key = doc.storage_key

    with transaction(runtime.sessions) as db:
        db.execute(delete(Chunk).where(Chunk.document_id == document_id))
        # Đoạn trích nguyên văn trong citation là nội dung tài liệu: xóa luôn, chỉ giữ tên và số trang
        db.execute(
            update(Citation).where(Citation.document_id == document_id).values(cited_text=None)
        )

    runtime.file_store.delete(key)

    with transaction(runtime.sessions) as db:
        db.execute(
            update(Document)
            .where(Document.id == document_id, Document.status == "deleting")
            .values(status="deleted", purged_at=datetime.now(UTC))
        )
    log.info("purge_done", document_id=str(document_id))
