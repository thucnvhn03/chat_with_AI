"""Adapter embedding giả lập, tất định, không cần tải mô hình.

Băm từng từ (đã chuẩn hóa chữ thường, NFC) vào một ô của vector rồi chuẩn hóa độ dài 1, nên hai văn
bản chung nhiều từ có độ tương đồng cosine cao. Chỉ dùng cho kiểm thử tự động và E2E, KHÔNG dùng để
đánh giá chất lượng truy xuất.
"""

import hashlib
import math
import re
import unicodedata

_WORD = re.compile(r"\w+", re.UNICODE)
_TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def _words(text: str) -> list[str]:
    return _WORD.findall(unicodedata.normalize("NFC", text).lower())


class HashEmbeddingProvider:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dimension
        for word in _words(text):
            digest = hashlib.blake2b(word.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            vec[index] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            # Văn bản không có từ nào: vector đơn vị cố định để không chia cho 0
            vec[0] = 1.0
            return vec
        return [x / norm for x in vec]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def count_tokens(self, texts: list[str]) -> list[int]:
        return [len(_TOKEN.findall(t)) for t in texts]
