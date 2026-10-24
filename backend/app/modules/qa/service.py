"""Điều phối hỏi đáp có nguồn và cơ chế từ chối (M-06; implement_plan.md mục 5.3; ADR-002, ADR-011).

Ba lớp từ chối — mọi trường hợp đều đặt `not_found = True`:
  1. Không có chunk nào, hoặc điểm cao nhất < MIN_RELEVANCE_SCORE → KHÔNG gọi mô hình sinh.
  2. Mô hình trả đúng câu từ chối cố định (so khớp chính xác sau khi chuẩn hóa).
  3. Câu trả lời có nội dung nhưng không có citation hợp lệ nào (BR-012: 100% câu trả lời có nội dung
     phải có nguồn).

Mô-đun này không đọc kho tệp (SADD 3.1): chỉ dùng chunk đã truy xuất.
"""

import re
import time
import unicodedata
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from opentelemetry import trace

from app.modules.retrieval.search import RetrievedChunk
from app.observability.metrics import QA_STEP_LATENCY
from app.ports.ai import AnswerGenerator, EmbeddingProvider, SourceChunk

NOT_FOUND_SENTENCE = "Không tìm thấy thông tin này trong các tài liệu đã tải lên."

tracer = trace.get_tracer("app.qa")


@dataclass(frozen=True)
class CitationResult:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    page: int
    cited_text: str


@dataclass
class QAResult:
    answer: str
    not_found: bool
    citations: list[CitationResult] = field(default_factory=list)
    # Lý do từ chối để đo lường: below_threshold | model_not_found | no_valid_citation | None
    reason: str | None = None
    refused: bool = False
    generator_called: bool = False
    timings_ms: dict[str, int] = field(default_factory=dict)


Retriever = Callable[[list[float]], list[RetrievedChunk]]

_SPACES = re.compile(r"\s+")
_QUOTES = "\"'“”‘’«»「」"


def normalize_for_match(text: str) -> str:
    text = unicodedata.normalize("NFC", text).strip().strip(_QUOTES).strip()
    return _SPACES.sub(" ", text).lower()


_NOT_FOUND_NORMALIZED = normalize_for_match(NOT_FOUND_SENTENCE)


def is_not_found_sentence(text: str) -> bool:
    return normalize_for_match(text) == _NOT_FOUND_NORMALIZED


def retrieval_query(question: str, history: list[dict[str, str]]) -> str:
    """Câu hỏi hiện tại ghép với câu hỏi của người dùng ở lượt trước (US-010, mục 5.3 bước 4)."""
    previous = next((m["content"] for m in reversed(history) if m["role"] == "user"), None)
    return f"{previous}\n{question}" if previous else question


@contextmanager
def _step(name: str, timings: dict[str, int]) -> Iterator[None]:
    start = time.perf_counter()
    with tracer.start_as_current_span(f"qa.{name}"):
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            QA_STEP_LATENCY.labels(name).observe(elapsed)
            timings[name] = int(elapsed * 1000)


def map_citations(raw: list[tuple[int, str]], chunks: list[RetrievedChunk]) -> list[CitationResult]:
    """Ánh xạ (chỉ số chunk, cited_text) → tài liệu và trang; bỏ chỉ số sai; gộp trùng (tài liệu, trang)."""
    seen: set[tuple[uuid.UUID, int]] = set()
    result: list[CitationResult] = []
    for index, cited_text in raw:
        if not 0 <= index < len(chunks):
            continue
        chunk = chunks[index]
        key = (chunk.document_id, chunk.page)
        if key in seen:
            continue
        seen.add(key)
        result.append(
            CitationResult(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_name=chunk.document_name,
                page=chunk.page,
                cited_text=cited_text.strip(),
            )
        )
    return result


def answer_question(
    question: str,
    history: list[dict[str, str]],
    embedder: EmbeddingProvider,
    retrieve: Retriever,
    generator: AnswerGenerator,
    min_relevance_score: float,
    timeout_s: float,
) -> QAResult:
    timings: dict[str, int] = {}
    deadline = time.monotonic() + timeout_s
    question = unicodedata.normalize("NFC", question).strip()

    with _step("embed", timings):
        query_vector = embedder.embed([retrieval_query(question, history)])[0]
    with _step("retrieve", timings):
        chunks = retrieve(query_vector)

    # Lớp 1: không có gì đủ liên quan → không gọi mô hình
    if not chunks or max(c.score for c in chunks) < min_relevance_score:
        return QAResult(NOT_FOUND_SENTENCE, True, reason="below_threshold", timings_ms=timings)

    sources = [SourceChunk(str(c.chunk_id), c.document_name, c.page, c.text) for c in chunks]
    with _step("generate", timings):
        generated = generator.generate(
            question, history, sources, timeout_s=max(1.0, deadline - time.monotonic())
        )

    if generated.refused:
        return QAResult("", False, refused=True, generator_called=True, timings_ms=timings)
    # Lớp 2: mô hình trả câu từ chối cố định
    if not generated.text.strip() or is_not_found_sentence(generated.text):
        return QAResult(
            NOT_FOUND_SENTENCE,
            True,
            reason="model_not_found",
            generator_called=True,
            timings_ms=timings,
        )
    citations = map_citations(generated.citations, chunks)
    # Lớp 3: có nội dung nhưng không có nguồn hợp lệ
    if not citations:
        return QAResult(
            NOT_FOUND_SENTENCE,
            True,
            reason="no_valid_citation",
            generator_called=True,
            timings_ms=timings,
        )
    return QAResult(
        generated.text.strip(), False, citations, generator_called=True, timings_ms=timings
    )
