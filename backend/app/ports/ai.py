"""Cổng AI (P-01): embedding và sinh câu trả lời. Đổi Kịch bản A/B (OQ-006) chỉ cần đổi adapter."""

from dataclasses import dataclass, field
from typing import Protocol


class EmbeddingProvider(Protocol):
    dimension: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Vector đã chuẩn hóa độ dài 1 (dùng khoảng cách cosine)."""
        ...

    def count_tokens(self, texts: list[str]) -> list[int]:
        """Số token của từng chuỗi theo bộ tách từ của mô hình (dùng khi cắt chunk)."""
        ...


@dataclass
class SourceChunk:
    chunk_id: str
    document_name: str
    page: int
    text: str


@dataclass
class GeneratedAnswer:
    text: str
    # (chỉ số chunk trong danh sách đầu vào, cited_text)
    citations: list[tuple[int, str]] = field(default_factory=list)
    # Mô hình từ chối vì lý do an toàn (stop_reason = "refusal")
    refused: bool = False


class AnswerGenerationError(Exception):
    """Dịch vụ sinh câu trả lời lỗi (mạng, hạn mức, phản hồi bị cắt...)."""


class AnswerTimeoutError(AnswerGenerationError):
    """Quá ANSWER_TIMEOUT_S."""


class AnswerGenerator(Protocol):
    def generate(
        self,
        question: str,
        history: list[dict[str, str]],
        chunks: list[SourceChunk],
        timeout_s: float,
    ) -> GeneratedAnswer:
        """`history`: các lượt trước dạng {"role": "user"|"assistant", "content": "..."}."""
        ...
