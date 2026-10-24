"""T2-04: ba lớp từ chối, ánh xạ citation, ghép câu hỏi trước (dùng fake_llm, không cần cơ sở dữ liệu)."""

import uuid

from app.adapters.fake_llm import NOT_FOUND_SENTENCE, FakeAnswerGenerator
from app.adapters.hash_embedding import HashEmbeddingProvider
from app.modules.qa.service import (
    answer_question,
    is_not_found_sentence,
    map_citations,
    retrieval_query,
)
from app.modules.retrieval.search import RetrievedChunk

DOC_A, DOC_B = uuid.uuid4(), uuid.uuid4()
embedder = HashEmbeddingProvider(64)


def _chunk(doc: uuid.UUID, name: str, page: int, text: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(uuid.uuid4(), doc, name, page, text, score)


CHUNKS = [
    _chunk(DOC_A, "HopDong_A.pdf", 5, "Thời hạn thanh toán là 30 ngày. Phạt chậm 0,05%/ngày.", 0.8),
    _chunk(DOC_B, "BaoGia_B.pdf", 2, "Giá gói tiêu chuẩn là 12 triệu đồng mỗi tháng.", 0.6),
]


def _ask(gen: FakeAnswerGenerator, chunks: list[RetrievedChunk], threshold: float = 0.3):  # type: ignore[no-untyped-def]
    return answer_question(
        "Thời hạn thanh toán là bao lâu?",
        [],
        embedder,
        lambda _v: chunks,
        gen,
        min_relevance_score=threshold,
        timeout_s=10,
    )


def test_answer_with_citation() -> None:
    gen = FakeAnswerGenerator()
    result = _ask(gen, CHUNKS)
    assert not result.not_found
    assert result.answer == "Thời hạn thanh toán là 30 ngày."
    assert len(result.citations) == 1
    c = result.citations[0]
    assert (c.document_id, c.document_name, c.page) == (DOC_A, "HopDong_A.pdf", 5)
    assert set(result.timings_ms) == {"embed", "retrieve", "generate"}


def test_layer1_below_threshold_does_not_call_model() -> None:
    gen = FakeAnswerGenerator()
    result = _ask(gen, CHUNKS, threshold=0.95)
    assert result.not_found and result.reason == "below_threshold"
    assert result.answer == NOT_FOUND_SENTENCE
    assert gen.calls == 0


def test_layer1_no_chunks_does_not_call_model() -> None:
    gen = FakeAnswerGenerator()
    result = _ask(gen, [])
    assert result.not_found and gen.calls == 0


def test_layer2_fixed_refusal_sentence() -> None:
    result = _ask(FakeAnswerGenerator("not_found_sentence"), CHUNKS)
    assert result.not_found and result.reason == "model_not_found"
    assert result.citations == []


def test_layer3_content_without_citation() -> None:
    result = _ask(FakeAnswerGenerator("no_citations"), CHUNKS)
    assert result.not_found and result.reason == "no_valid_citation"
    assert result.answer == NOT_FOUND_SENTENCE


def test_layer3_citation_index_out_of_range_is_invalid() -> None:
    result = _ask(FakeAnswerGenerator("bad_index"), CHUNKS)
    assert result.not_found and result.reason == "no_valid_citation"


def test_refused_is_not_not_found() -> None:
    result = _ask(FakeAnswerGenerator("refuse"), CHUNKS)
    assert result.refused and not result.not_found


def test_answer_with_content_always_has_citation() -> None:
    for mode in ("cite", "no_citations", "bad_index", "not_found_sentence"):
        result = _ask(FakeAnswerGenerator(mode), CHUNKS)  # type: ignore[arg-type]
        assert result.not_found or len(result.citations) >= 1


def test_map_citations_dedupes_and_keeps_order() -> None:
    extra = _chunk(DOC_A, "HopDong_A.pdf", 5, "đoạn khác cùng trang", 0.5)
    chunks = [*CHUNKS, extra]
    mapped = map_citations(
        [(1, "giá"), (0, "thời hạn"), (2, "trùng trang"), (0, "lặp"), (9, "sai")], chunks
    )
    assert [(c.document_name, c.page) for c in mapped] == [
        ("BaoGia_B.pdf", 2),
        ("HopDong_A.pdf", 5),
    ]
    assert mapped[1].cited_text == "thời hạn"


def test_not_found_sentence_matching_is_normalized() -> None:
    assert is_not_found_sentence(
        "  “Không tìm thấy thông tin này trong các tài liệu   đã tải lên.” "
    )
    assert not is_not_found_sentence("Không tìm thấy thông tin này. Tuy nhiên, giá là 12 triệu.")


def test_retrieval_query_appends_previous_user_question() -> None:
    history = [
        {"role": "user", "content": "Hợp đồng A có điều khoản phạt không?"},
        {"role": "assistant", "content": "Có."},
    ]
    assert retrieval_query("Mức phạt là bao nhiêu?", history) == (
        "Hợp đồng A có điều khoản phạt không?\nMức phạt là bao nhiêu?"
    )
    assert retrieval_query("Câu đầu", []) == "Câu đầu"
