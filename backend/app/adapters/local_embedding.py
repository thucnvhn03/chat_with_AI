"""Adapter embedding chạy nội bộ bằng sentence-transformers (mặc định `BAAI/bge-m3`, 1024 chiều).

Mô hình nạp một lần khi tiến trình khởi động (ứng dụng: nhúng câu hỏi; worker: nhúng chunk). Dữ liệu
không rời hạ tầng ở bước này, ở cả Kịch bản A và B.
"""

import threading
from typing import Any


class LocalEmbeddingProvider:
    def __init__(self, model_name: str, dimension: int, batch_size: int) -> None:
        from sentence_transformers import SentenceTransformer  # nạp chậm: thư viện nặng

        self._model: Any = SentenceTransformer(model_name, device="cpu")
        actual = self._model.get_sentence_embedding_dimension()
        if actual != dimension:
            raise ValueError(
                f"EMBEDDING_DIM={dimension} không khớp số chiều của mô hình {model_name} ({actual})"
            )
        self.dimension = dimension
        self._batch_size = batch_size
        # Nhiều luồng worker dùng chung một mô hình; khóa để tránh tranh chấp bộ nhớ của torch
        self._lock = threading.Lock()

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        with self._lock:
            vectors = self._model.encode(
                texts,
                batch_size=self._batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        return [[float(x) for x in row] for row in vectors]

    def count_tokens(self, texts: list[str]) -> list[int]:
        if not texts:
            return []
        encoded = self._model.tokenizer(texts, add_special_tokens=False)["input_ids"]
        return [len(ids) for ids in encoded]
