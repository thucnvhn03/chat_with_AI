"""T2-03: adapter Claude với phản hồi SDK được giả lập; kiểm thử thật đánh dấu needs_api_key."""

import os
from types import SimpleNamespace
from typing import Any

import pytest

from app.adapters.claude_llm import (
    FALLBACK_BETA,
    SYSTEM_PROMPT,
    ClaudeAnswerGenerator,
    build_documents,
    parse_response,
)
from app.ports.ai import AnswerGenerationError, SourceChunk

CHUNKS = [
    SourceChunk("c1", "HopDong_A.pdf", 5, "Thời hạn thanh toán là 30 ngày."),
    SourceChunk("c2", "BaoGia_B.pdf", 2, "Giá gói tiêu chuẩn là 12 triệu đồng."),
]


def _cit(index: int, text: str) -> Any:
    return SimpleNamespace(type="char_location", document_index=index, cited_text=text)


def _response(content: list[Any], stop_reason: str = "end_turn") -> Any:
    usage = SimpleNamespace(input_tokens=10, output_tokens=5, cache_read_input_tokens=0)
    return SimpleNamespace(content=content, stop_reason=stop_reason, usage=usage, model="m")


def test_citations_map_to_chunk_index() -> None:
    response = _response(
        [
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text="Theo hợp đồng, ", citations=None),
            SimpleNamespace(
                type="text", text="thời hạn là 30 ngày", citations=[_cit(0, "30 ngày")]
            ),
            SimpleNamespace(type="text", text=" và giá 12 triệu.", citations=[_cit(1, "12 triệu")]),
        ]
    )
    answer = parse_response(response)
    assert answer.text == "Theo hợp đồng, thời hạn là 30 ngày và giá 12 triệu."
    assert answer.citations == [(0, "30 ngày"), (1, "12 triệu")]
    assert not answer.refused


def test_refusal_is_reported_before_reading_content() -> None:
    response = _response([SimpleNamespace(type="text", text="một phần", citations=None)], "refusal")
    response.stop_details = SimpleNamespace(category="cyber")
    answer = parse_response(response)
    assert answer.refused and answer.text == "" and answer.citations == []


def test_max_tokens_is_an_error() -> None:
    with pytest.raises(AnswerGenerationError):
        parse_response(_response([], "max_tokens"))


def test_documents_have_title_and_citations_enabled() -> None:
    docs = build_documents(CHUNKS)
    assert docs[0]["title"] == "HopDong_A.pdf — trang 5"
    assert docs[1]["citations"] == {"enabled": True}
    assert docs[0]["source"] == {
        "type": "text",
        "media_type": "text/plain",
        "data": "Thời hạn thanh toán là 30 ngày.",
    }


class _RecordingClient:
    def __init__(self) -> None:
        self.kwargs: dict[str, Any] = {}
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))
        self.messages = SimpleNamespace(create=self._create)

    def with_options(self, **_: Any) -> "_RecordingClient":
        return self

    def _create(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        return _response([SimpleNamespace(type="text", text="ok", citations=[_cit(0, "x")])])


def test_request_shape() -> None:
    client = _RecordingClient()
    gen = ClaudeAnswerGenerator("claude-opus-5-5", "medium", 16000, 2, True, client=client)
    history = [{"role": "user", "content": "trước"}, {"role": "assistant", "content": "đáp"}]
    gen.generate("Câu hỏi?", history, CHUNKS, timeout_s=30)
    kw = client.kwargs
    assert kw["model"] == "claude-opus-5-5"
    assert kw["output_config"] == {"effort": "medium"}
    assert kw["betas"] == [FALLBACK_BETA] and kw["fallbacks"] == "default"
    # Không đặt thinking, không prefill, không structured outputs
    assert "thinking" not in kw
    assert "format" not in kw["output_config"]
    assert kw["messages"][-1]["role"] == "user"
    assert kw["system"][0]["text"] == SYSTEM_PROMPT
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert kw["messages"][:2] == history
    last = kw["messages"][-1]["content"]
    assert [b["type"] for b in last] == ["document", "document", "text"]


@pytest.mark.needs_api_key
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="cần ANTHROPIC_API_KEY")
def test_real_api_cites_correct_chunk() -> None:
    gen = ClaudeAnswerGenerator("claude-opus-5-5", "low", 4000, 2, True)
    answer = gen.generate("Giá gói tiêu chuẩn là bao nhiêu?", [], CHUNKS, timeout_s=120)
    assert not answer.refused
    assert any(index == 1 for index, _ in answer.citations)
