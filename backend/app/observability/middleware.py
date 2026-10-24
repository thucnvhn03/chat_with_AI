"""Middleware: ID yêu cầu, log truy cập không chứa thân yêu cầu, số liệu HTTP."""

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.observability.logging import get_logger
from app.observability.metrics import HTTP_LATENCY, HTTP_REQUESTS

log = get_logger("http")

REQUEST_ID_HEADER = "X-Request-ID"


def _route_template(request: Request) -> str:
    # Dùng mẫu đường dẫn (/documents/{document_id}) thay vì đường dẫn thật để số liệu không bùng nổ nhãn.
    # Router ghi route khớp vào scope sau khi định tuyến; thay từng đoạn đường dẫn trùng giá trị tham số
    # bằng tên tham số.
    if request.scope.get("route") is None:
        return "unmatched"
    values = {str(v): k for k, v in request.scope.get("path_params", {}).items()}
    segments = request.url.path.split("/")
    return "/".join("{" + values[s] + "}" if s in values else s for s in segments)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Gắn ID yêu cầu vào log và phản hồi; ghi một dòng log truy cập cho mỗi yêu cầu.

    Log truy cập chỉ gồm phương thức, mẫu đường dẫn, mã trạng thái và thời gian. Thân yêu cầu không bao
    giờ được ghi — đặc biệt với POST /documents (tệp) và POST /conversations/*/messages (câu hỏi).
    Chuỗi truy vấn cũng không được ghi.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            elapsed = time.perf_counter() - start
            route = _route_template(request)
            HTTP_REQUESTS.labels(request.method, route, str(status)).inc()
            HTTP_LATENCY.labels(request.method, route).observe(elapsed)
            log.info(
                "http_request",
                method=request.method,
                route=route,
                status=status,
                duration_ms=round(elapsed * 1000, 1),
            )
