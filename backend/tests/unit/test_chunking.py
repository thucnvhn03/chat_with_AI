"""T1-14: cắt chunk theo trang."""

import pytest

from app.adapters.hash_embedding import HashEmbeddingProvider
from app.modules.ingestion.chunking import chunk_page, chunk_pages, split_pieces
from app.modules.ingestion.extract import PageText

count = HashEmbeddingProvider(8).count_tokens


def _page(n: int, words: int, prefix: str = "w") -> PageText:
    return PageText(n, " ".join(f"{prefix}{n}x{i}" for i in range(words)))


def test_no_chunk_spans_two_pages() -> None:
    pages = [_page(1, 230, "a"), _page(2, 75, "b"), _page(3, 10, "c")]
    chunks = chunk_pages(pages, count, chunk_tokens=50, overlap=10)
    for c in chunks:
        prefixes = {w[0] for w in c.text.split()}
        assert len(prefixes) == 1
        assert prefixes == {"abc"[c.page - 1]}
    assert [c.ordinal for c in chunks] == list(range(len(chunks)))


def test_short_page_gives_exactly_one_chunk() -> None:
    chunks = chunk_page(PageText(4, "Một trang rất ngắn."), count, 50, 10)
    assert len(chunks) == 1
    assert chunks[0].page == 4 and chunks[0].text == "Một trang rất ngắn."


def test_empty_page_gives_no_chunk() -> None:
    assert chunk_page(PageText(1, ""), count, 50, 10) == []
    assert chunk_page(PageText(1, "   \n  "), count, 50, 10) == []


def test_chunks_respect_token_limit_and_overlap() -> None:
    page = _page(1, 500)
    chunks = chunk_page(page, count, chunk_tokens=40, overlap=8)
    assert len(chunks) > 1
    for c in chunks:
        assert sum(count([w])[0] for w in c.text.split()) <= 40
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        assert nxt.start_piece < prev.end_piece  # có chồng lấp
        assert nxt.start_piece > prev.start_piece  # luôn tiến


def test_chunks_without_overlap_reconstruct_page_text() -> None:
    text = (
        "Điều 1. Phạm vi.\nBên A cung cấp   dịch vụ.\n\nĐiều 2. Giá trị hợp đồng là 1,2 tỷ đồng. "
        * 30
    )
    page = PageText(1, text.strip())
    chunks = chunk_page(page, count, chunk_tokens=30, overlap=7)
    pieces = split_pieces(page.text)
    rebuilt = ""
    covered = 0
    for c in chunks:
        rebuilt += "".join(pieces[max(c.start_piece, covered) : c.end_piece])
        covered = c.end_piece
    assert rebuilt.strip() == page.text
    assert covered == len(pieces)


def test_invalid_parameters() -> None:
    with pytest.raises(ValueError):
        chunk_page(_page(1, 5), count, 10, 10)
    with pytest.raises(ValueError):
        chunk_page(_page(1, 5), count, 0, 0)
