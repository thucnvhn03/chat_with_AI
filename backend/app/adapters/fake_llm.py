"""Adapter AnswerGenerator giả lập, trả câu trả lời và citation định sẵn (kiểm thử, E2E, dev không có khóa).

Hành vi mặc định: trong chunk có nhiều từ chung với câu hỏi nhất, trích câu khớp nhất, kèm citation trỏ đúng
chunk đó. Kiểm thử có thể đặt `mode` để giả lập các trường hợp từ chối.
"""

import re
import unicodedata
from typing import Literal

from app.ports.ai import AnswerTimeoutError, GeneratedAnswer, SourceChunk

NOT_FOUND_SENTENCE = "Không tìm thấy thông tin này trong các tài liệu đã tải lên."

FakeMode = Literal["cite", "not_found_sentence", "no_citations", "refuse", "bad_index", "timeout"]

_WORD = re.compile(r"\w+", re.UNICODE)
_SENTENCE = re.compile(r"(?<=[.!?…])\s+")


def _words(text: str) -> set[str]:
    return set(_WORD.findall(unicodedata.normalize("NFC", text).lower()))


class FakeAnswerGenerator:
    def __init__(self, mode: FakeMode = "cite") -> None:
        self.mode: FakeMode = mode
        self.calls = 0
        self.last_history: list[dict[str, str]] = []
        self.last_chunks: list[SourceChunk] = []

    def generate(
        self,
        question: str,
        history: list[dict[str, str]],
        chunks: list[SourceChunk],
        timeout_s: float,
    ) -> GeneratedAnswer:
        self.calls += 1
        self.last_history = history
        self.last_chunks = chunks
        if self.mode == "timeout":
            raise AnswerTimeoutError("timeout")
        if self.mode == "refuse":
            return GeneratedAnswer(text="", refused=True)
        if self.mode == "not_found_sentence" or not chunks:
            return GeneratedAnswer(text=NOT_FOUND_SENTENCE)
        if self.mode == "no_citations":
            return GeneratedAnswer(text="Câu trả lời không có nguồn.")
        if self.mode == "bad_index":
            return GeneratedAnswer(text="Câu trả lời.", citations=[(len(chunks) + 5, "x")])

        q = _words(question)
        best = max(range(len(chunks)), key=lambda i: len(q & _words(chunks[i].text)))
        sentences = [s for s in _SENTENCE.split(chunks[best].text.strip()) if s]
        sentence = max(sentences, key=lambda s: len(q & _words(s)))
        return GeneratedAnswer(text=sentence, citations=[(best, sentence)])
