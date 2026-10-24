"""Sinh bộ PDF tổng hợp cho kiểm thử (implement_plan.md mục 9.2).

Không commit tệp nhị phân: mỗi PDF được sinh lúc chạy kiểm thử từ văn bản cho trước. Phông DejaVu
(có đủ dấu tiếng Việt) lấy từ hệ thống; ảnh dev và máy chạy CI Ubuntu đều có sẵn.
"""

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
]

_font_name: str | None = None


def _font() -> str:
    global _font_name
    if _font_name is None:
        for path in FONT_CANDIDATES:
            if path.exists():
                pdfmetrics.registerFont(TTFont("TestSans", str(path)))
                _font_name = "TestSans"
                break
        else:
            raise RuntimeError("Không tìm thấy phông Unicode để sinh PDF kiểm thử")
    return _font_name


def _wrap(text: str, width: int = 90) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > width:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}".strip()
        lines.append(line)
    return lines


def make_pdf(pages: list[str]) -> bytes:
    """Mỗi phần tử là văn bản của một trang."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    font = _font()
    for text in pages:
        c.setFont(font, 10)
        y = 800
        for line in _wrap(text):
            c.drawString(40, y, line)
            y -= 14
            if y < 40:
                break
        c.showPage()
    c.save()
    return buffer.getvalue()


def make_image_only_pdf(pages: int = 2) -> bytes:
    """PDF "dạng scan": chỉ có hình vẽ, không có lớp văn bản."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    for i in range(pages):
        for k in range(20):
            c.rect(40 + k * 5, 400 + i * 10, 200, 100, fill=k % 2)
        c.showPage()
    c.save()
    return buffer.getvalue()


def make_encrypted_pdf(pages: list[str], password: str = "mat-khau") -> bytes:
    writer = PdfWriter(clone_from=PdfReader(io.BytesIO(make_pdf(pages))))
    writer.encrypt(user_password=password, owner_password=password + "-owner", algorithm="AES-256")
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def make_corrupted_pdf() -> bytes:
    """Bắt đầu bằng %PDF- (qua được kiểm tra phía tải lên) nhưng nội dung hỏng."""
    good = make_pdf(["Tài liệu sẽ bị hỏng."])
    return good[:40] + b"\x00garbage\x00" * 50


NOT_A_PDF = b"Day la tep van ban doi duoi thanh .pdf\n"
