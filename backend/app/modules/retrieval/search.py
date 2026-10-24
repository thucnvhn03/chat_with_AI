"""Truy xuất theo quyền (M-07; implement_plan.md mục 5.2; ADR-004).

- Bộ lọc quyền nằm TRONG câu truy vấn (`d.id = ANY(:allowed)`), không lọc sau khi lấy kết quả.
- Chỉ lấy tài liệu `ready`: tài liệu `deleting` không bao giờ được truy xuất (BR-005, AC-005).
- Bật `hnsw.iterative_scan` (pgvector ≥ 0.8) và tăng `ef_search` để khi danh sách tài liệu được phép
  nhỏ trong một kho lớn, chỉ mục HNSW vẫn trả đủ `top_k` kết quả.
- `MAX_CHUNKS_PER_DOC` (0 = tắt) giới hạn số chunk mỗi tài liệu để không một tài liệu nào chiếm hết
  kết quả (US-009).
"""

import uuid
from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

# Lấy dư ứng viên rồi mới giới hạn theo tài liệu
CANDIDATE_FACTOR = 4


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page: int
    text: str
    score: float  # 1 - khoảng cách cosine


_SEARCH_SQL = text(
    """
    WITH candidates AS (
      SELECT c.id, c.document_id, d.file_name, c.page, c.text,
             c.embedding <=> CAST(:query AS vector) AS distance
      FROM chunks c
      JOIN documents d ON d.id = c.document_id
      WHERE d.status = 'ready'
        AND d.id = ANY(:allowed)
      ORDER BY c.embedding <=> CAST(:query AS vector)
      LIMIT :candidates
    ), ranked AS (
      SELECT *, row_number() OVER (PARTITION BY document_id ORDER BY distance) AS rank_in_doc
      FROM candidates
    )
    SELECT id, document_id, file_name, page, text, 1 - distance AS score
    FROM ranked
    WHERE :per_doc = 0 OR rank_in_doc <= :per_doc
    ORDER BY distance, id
    LIMIT :top_k
    """
)


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.7g}" for v in values) + "]"


def search(
    db: Session,
    query_embedding: list[float],
    allowed_document_ids: Iterable[uuid.UUID],
    top_k: int,
    max_chunks_per_doc: int = 0,
    ef_search: int = 100,
) -> list[RetrievedChunk]:
    allowed = list(allowed_document_ids)
    if not allowed or top_k <= 0:
        return []
    # SET LOCAL chỉ có hiệu lực trong giao dịch hiện tại
    db.execute(text("SET LOCAL hnsw.iterative_scan = 'relaxed_order'"))
    db.execute(text(f"SET LOCAL hnsw.ef_search = {max(int(ef_search), top_k)}"))
    rows = db.execute(
        _SEARCH_SQL,
        {
            "query": _vector_literal(query_embedding),
            "allowed": allowed,
            "candidates": top_k * CANDIDATE_FACTOR if max_chunks_per_doc > 0 else top_k,
            "per_doc": max(0, max_chunks_per_doc),
            "top_k": top_k,
        },
    ).all()
    return [
        RetrievedChunk(
            chunk_id=r.id,
            document_id=r.document_id,
            document_name=r.file_name,
            page=r.page,
            text=r.text,
            score=float(r.score),
        )
        for r in rows
    ]
