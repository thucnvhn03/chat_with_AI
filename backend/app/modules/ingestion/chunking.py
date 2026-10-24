"""Cắt chunk theo trang (M-05).

- Không chunk nào vượt qua ranh giới trang: mỗi chunk thuộc đúng một trang (citation đúng trang).
- Mỗi chunk tối đa `chunk_tokens` token, chồng lấp `overlap` token với chunk trước trong cùng trang.
- Văn bản được tách thành các mảnh "từ + khoảng trắng theo sau", nên ghép các phần không chồng lấp của
  các chunk lại đúng bằng văn bản trang.
- Đếm token bằng bộ đếm của mô hình embedding (truyền vào), để chunk không vượt độ dài mô hình nhận.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass

from app.modules.ingestion.extract import PageText

TokenCounter = Callable[[list[str]], list[int]]

_PIECE = re.compile(r"\S+\s*")


@dataclass(frozen=True)
class TextChunk:
    page: int
    ordinal: int
    text: str
    # Vị trí mảnh bắt đầu/kết thúc trong trang (phục vụ kiểm thử ghép lại văn bản)
    start_piece: int
    end_piece: int


def split_pieces(text: str) -> list[str]:
    return _PIECE.findall(text)


def chunk_page(
    page: PageText,
    count_tokens: TokenCounter,
    chunk_tokens: int,
    overlap: int,
    first_ordinal: int = 0,
) -> list[TextChunk]:
    if chunk_tokens <= 0:
        raise ValueError("chunk_tokens phải > 0")
    if not 0 <= overlap < chunk_tokens:
        raise ValueError("overlap phải trong khoảng [0, chunk_tokens)")
    pieces = split_pieces(page.text)
    if not pieces:
        return []
    # Đếm token từng mảnh (một mảnh dài hơn giới hạn vẫn được giữ nguyên thành một chunk riêng)
    sizes = [max(1, n) for n in count_tokens([p.strip() for p in pieces])]

    chunks: list[TextChunk] = []
    start = 0
    ordinal = first_ordinal
    while start < len(pieces):
        end = start
        total = 0
        while end < len(pieces) and (total + sizes[end] <= chunk_tokens or end == start):
            total += sizes[end]
            end += 1
        text = "".join(pieces[start:end]).strip()
        chunks.append(TextChunk(page.page, ordinal, text, start, end))
        ordinal += 1
        if end >= len(pieces):
            break
        # Lùi lại để chồng lấp khoảng `overlap` token, nhưng luôn tiến ít nhất một mảnh
        back = end
        carried = 0
        while back > start + 1 and carried + sizes[back - 1] <= overlap:
            back -= 1
            carried += sizes[back]
        start = back
    return chunks


def chunk_pages(
    pages: list[PageText], count_tokens: TokenCounter, chunk_tokens: int, overlap: int
) -> list[TextChunk]:
    result: list[TextChunk] = []
    for page in pages:
        result.extend(chunk_page(page, count_tokens, chunk_tokens, overlap, len(result)))
    return result
