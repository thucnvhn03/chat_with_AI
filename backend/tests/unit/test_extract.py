"""T1-13: trích xuất PDF theo trang trên bộ PDF tổng hợp."""

import unicodedata

import pytest

from app.modules.ingestion.extract import (
    ExtractionError,
    extract_page,
    extract_pages,
    normalize_text,
)
from tests import pdf_factory

MIN_CHARS = 20


def test_plain_pdf_keeps_page_numbers() -> None:
    data = pdf_factory.make_pdf(["Trang mot noi dung A.", "Trang hai noi dung B.", "Trang ba C."])
    pages = extract_pages(data, MIN_CHARS)
    assert [p.page for p in pages] == [1, 2, 3]
    assert "noi dung B" in pages[1].text


def test_vietnamese_text_is_nfc_and_keeps_diacritics() -> None:
    sentence = "Hợp đồng phân phối có hiệu lực 24 tháng kể từ ngày ký."
    # Văn bản đầu vào ở dạng tổ hợp (NFD) vẫn phải ra dạng dựng sẵn (NFC)
    data = pdf_factory.make_pdf([unicodedata.normalize("NFD", sentence)])
    pages = extract_pages(data, MIN_CHARS)
    assert pages[0].text == unicodedata.normalize("NFC", pages[0].text)
    assert "Hợp đồng phân phối" in pages[0].text
    assert "24 tháng" in pages[0].text


def test_encrypted_pdf() -> None:
    data = pdf_factory.make_encrypted_pdf(["Nội dung mật của hợp đồng."])
    with pytest.raises(ExtractionError) as exc:
        extract_pages(data, MIN_CHARS)
    assert exc.value.reason == "encrypted"


def test_corrupted_pdf() -> None:
    with pytest.raises(ExtractionError) as exc:
        extract_pages(pdf_factory.make_corrupted_pdf(), MIN_CHARS)
    assert exc.value.reason == "corrupted"


def test_random_bytes_are_corrupted() -> None:
    with pytest.raises(ExtractionError) as exc:
        extract_pages(b"%PDF-1.7\n" + bytes(range(256)) * 20, MIN_CHARS)
    assert exc.value.reason == "corrupted"


def test_image_only_pdf_has_no_text() -> None:
    with pytest.raises(ExtractionError) as exc:
        extract_pages(pdf_factory.make_image_only_pdf(3), MIN_CHARS)
    assert exc.value.reason == "no_text"


def test_extract_single_page_and_out_of_range() -> None:
    data = pdf_factory.make_pdf(["Một", "Hai nội dung trang hai", "Ba"])
    text, total = extract_page(data, 2)
    assert total == 3 and "trang hai" in text
    with pytest.raises(IndexError):
        extract_page(data, 4)
    with pytest.raises(IndexError):
        extract_page(data, 0)


def test_normalize_whitespace() -> None:
    assert normalize_text("  a \t b  \r\n\n\n\n c\x00 ") == "a b\n\nc"
