"""Log JSON bằng structlog, có bộ lọc che nội dung (ADR-009).

Mọi trường có tên trong `REDACTED_KEYS` bị xóa khỏi bản ghi log, ở mọi độ sâu. Đây là lưới an toàn;
quy tắc chính vẫn là không truyền nội dung tài liệu/câu hỏi vào log.
"""

import logging
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any

import structlog

REDACTED_KEYS = frozenset(
    {"question", "content", "text", "body", "answer", "cited_text", "password", "history"}
)


def _strip(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _strip(v) for k, v in value.items() if k not in REDACTED_KEYS}
    if isinstance(value, list | tuple):
        return [_strip(v) for v in value]
    return value


def redact_content(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    for key in list(event_dict):
        if key in REDACTED_KEYS:
            del event_dict[key]
        else:
            event_dict[key] = _strip(event_dict[key])
    return event_dict


_configured = False


def configure_logging(level: str = "INFO") -> None:
    """Cấu hình structlog và chuyển log của thư viện chuẩn qua cùng bộ xử lý JSON."""
    global _configured
    if _configured:
        return
    shared: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        redact_content,
    ]
    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    _configured = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.stdlib.get_logger(name)
