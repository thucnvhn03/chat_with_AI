"""Adapter AnswerGenerator gọi Claude API (Kịch bản A, implement_plan.md mục 6.4).

Điểm chính:
- Mỗi chunk là một khối `document` văn bản bật `citations`; tiêu đề "tên tệp — trang N". Citation trả về
  mang `document_index` = chỉ số chunk trong danh sách đầu vào.
- `effort` đặt tường minh trong `output_config` (mặc định của claude-opus-5-5 là `medium`).
- KHÔNG đặt `thinking` (mô hình luôn suy nghĩ thích ứng), KHÔNG prefill, KHÔNG `output_config.format`
  (structured outputs không dùng chung được với citations).
- Đọc `stop_reason` trước nội dung: `refusal` → refused; `max_tokens` → lỗi.
- Chuyển mô hình dự phòng phía máy chủ khi bị từ chối: beta `server-side-fallback-2026-07-01`,
  `fallbacks="default"` (định tuyến theo nhóm lý do từ chối, không phải duy trì danh sách mô hình).
- Chỉ dẫn hệ thống cố định, đứng đầu, có `cache_control`. Chỉ dẫn ngắn hơn ngưỡng tối thiểu của bộ nhớ
  đệm thì không được lưu — đó không phải lỗi.

Dữ liệu rời hạ tầng ở bước này: các chunk được truy xuất, câu hỏi, ngữ cảnh hội thoại (ghi trong
docs/implement/data_handling.md).
"""

from typing import Any

import anthropic

from app.observability.logging import get_logger
from app.ports.ai import (
    AnswerGenerationError,
    AnswerTimeoutError,
    GeneratedAnswer,
    SourceChunk,
)

log = get_logger("adapters.claude")

FALLBACK_BETA = "server-side-fallback-2026-07-01"

SYSTEM_PROMPT = (
    "Bạn trả lời câu hỏi của nhân sự phát triển kinh doanh chỉ dựa trên các tài liệu được cung cấp "
    "trong yêu cầu này.\n"
    "Mỗi tài liệu là một đoạn trích có tiêu đề gồm tên tệp và số trang.\n"
    "Chỉ dùng thông tin có trong các đoạn trích đó và trích dẫn đoạn đã dùng cho mỗi ý.\n"
    "Nếu các đoạn trích không chứa thông tin để trả lời, hãy trả lời đúng một câu: "
    '"Không tìm thấy thông tin này trong các tài liệu đã tải lên."\n'
    "Không dùng kiến thức bên ngoài tài liệu. Trả lời bằng ngôn ngữ của câu hỏi."
)


def build_documents(chunks: list[SourceChunk]) -> list[dict[str, Any]]:
    return [
        {
            "type": "document",
            "source": {"type": "text", "media_type": "text/plain", "data": c.text},
            "title": f"{c.document_name} — trang {c.page}",
            "citations": {"enabled": True},
        }
        for c in chunks
    ]


def parse_response(response: Any) -> GeneratedAnswer:
    """Chuyển phản hồi của SDK thành GeneratedAnswer. Tách riêng để kiểm thử với phản hồi giả lập."""
    if response.stop_reason == "refusal":
        category = getattr(getattr(response, "stop_details", None), "category", None)
        log.warning("answer_refused", category=category)
        return GeneratedAnswer(text="", citations=[], refused=True)
    if response.stop_reason == "max_tokens":
        log.error("answer_truncated")
        raise AnswerGenerationError("max_tokens")

    text_parts: list[str] = []
    citations: list[tuple[int, str]] = []
    for block in response.content:
        if getattr(block, "type", None) != "text":
            continue  # bỏ qua khối thinking, fallback...
        text_parts.append(block.text)
        for cit in getattr(block, "citations", None) or []:
            index = getattr(cit, "document_index", None)
            if isinstance(index, int):
                citations.append((index, getattr(cit, "cited_text", "") or ""))
    return GeneratedAnswer(text="".join(text_parts), citations=citations, refused=False)


class ClaudeAnswerGenerator:
    def __init__(
        self,
        model: str,
        effort: str,
        max_tokens: int,
        max_retries: int,
        server_fallback: bool,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self._model = model
        self._effort = effort
        self._max_tokens = max_tokens
        self._server_fallback = server_fallback
        # Khóa API đọc từ biến môi trường ANTHROPIC_API_KEY hoặc kho bí mật, không ghi trong mã
        self._client = client or anthropic.Anthropic(api_key=api_key, max_retries=max_retries)

    def generate(
        self,
        question: str,
        history: list[dict[str, str]],
        chunks: list[SourceChunk],
        timeout_s: float,
    ) -> GeneratedAnswer:
        request: dict[str, Any] = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "output_config": {"effort": self._effort},
            "system": [
                {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
            ],
            "messages": [
                *history,
                {
                    "role": "user",
                    "content": [*build_documents(chunks), {"type": "text", "text": question}],
                },
            ],
        }
        client = self._client.with_options(timeout=timeout_s)
        try:
            if self._server_fallback:
                response = client.beta.messages.create(
                    betas=[FALLBACK_BETA], fallbacks="default", **request
                )
            else:
                response = client.messages.create(**request)
        except anthropic.RateLimitError as exc:
            log.warning("answer_rate_limited", request_id=_request_id(exc))
            raise AnswerGenerationError("rate_limited") from exc
        except anthropic.APIStatusError as exc:
            log.error("answer_api_error", status=exc.status_code, request_id=_request_id(exc))
            raise AnswerGenerationError(f"status_{exc.status_code}") from exc
        except anthropic.APITimeoutError as exc:
            log.warning("answer_timeout")
            raise AnswerTimeoutError("timeout") from exc
        except anthropic.APIConnectionError as exc:
            log.warning("answer_connection_error")
            raise AnswerGenerationError("connection") from exc

        usage = getattr(response, "usage", None)
        log.info(
            "answer_generated",
            model=getattr(response, "model", self._model),
            stop_reason=response.stop_reason,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", None),
        )
        return parse_response(response)


def _request_id(exc: anthropic.APIStatusError) -> str | None:
    return exc.response.headers.get("request-id") if exc.response is not None else None
