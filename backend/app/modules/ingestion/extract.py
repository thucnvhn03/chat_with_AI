"""Trích xuất văn bản PDF theo từng trang bằng `pypdf` (giấy phép BSD; chọn ở spike T0-06, ADR-010).

- Số trang bắt đầu từ 1 và luôn được giữ — nền tảng của citation (BR-019).
- Chuẩn hóa Unicode NFC (quan trọng với tiếng Việt: dấu tổ hợp và dấu dựng sẵn phải về một dạng) và
  khoảng trắng.
- Lỗi được phân loại thành `failure_reason` ổn định: `encrypted`, `corrupted`, `no_text`.
"""

import io
import re
import unicodedata
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import FileNotDecryptedError, PdfReadError


@dataclass(frozen=True)
class PageText:
    page: int
    text: str


class ExtractionError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


_INLINE_SPACE = re.compile(r"[ \t\f\v  -​　]+")
_MANY_NEWLINES = re.compile(r"\n{3,}")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0e-\x1f\x7f]")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = _CONTROL.sub("", text.replace("\r\n", "\n").replace("\r", "\n"))
    lines = [_INLINE_SPACE.sub(" ", line).strip() for line in text.split("\n")]
    return _MANY_NEWLINES.sub("\n\n", "\n".join(lines)).strip()


def open_pdf(data: bytes) -> PdfReader:
    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
    except FileNotDecryptedError as exc:
        raise ExtractionError("encrypted") from exc
    except Exception as exc:  # pypdf ném nhiều loại lỗi khác nhau với tệp hỏng
        raise ExtractionError("corrupted") from exc
    if reader.is_encrypted:
        # PDF chỉ có mật khẩu chủ sở hữu (mật khẩu mở rỗng) vẫn đọc được; còn lại là bị khóa
        try:
            if not reader.decrypt(""):
                raise ExtractionError("encrypted")
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError("encrypted") from exc
    return reader


def _page_text(reader: PdfReader, index: int) -> str:
    try:
        return normalize_text(reader.pages[index].extract_text() or "")
    except (FileNotDecryptedError, PermissionError) as exc:
        raise ExtractionError("encrypted") from exc
    except Exception as exc:
        raise ExtractionError("corrupted") from exc


def extract_pages(data: bytes, min_text_chars: int) -> list[PageText]:
    reader = open_pdf(data)
    try:
        count = len(reader.pages)
    except (PdfReadError, Exception) as exc:
        raise ExtractionError("corrupted") from exc
    if count == 0:
        raise ExtractionError("corrupted")
    pages = [PageText(page=i + 1, text=_page_text(reader, i)) for i in range(count)]
    if sum(len(p.text) for p in pages) < min_text_chars:
        # PDF dạng ảnh scan: chưa hỗ trợ ở MVP (ADR-010, OQ-007)
        raise ExtractionError("no_text")
    return pages


def page_count(data: bytes) -> int:
    return len(open_pdf(data).pages)


def extract_page(data: bytes, page: int) -> tuple[str, int]:
    """Văn bản của một trang (đánh số từ 1) và tổng số trang. Ngoài khoảng → IndexError."""
    reader = open_pdf(data)
    total = len(reader.pages)
    if page < 1 or page > total:
        raise IndexError(page)
    return _page_text(reader, page - 1), total
