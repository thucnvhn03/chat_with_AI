"""Định dạng lỗi chung của API: `{"error": {"code": ..., "message": ...}}` (implement_plan.md mục 4).

Lỗi chưa xử lý trả 500 với thông điệp chung; chi tiết kỹ thuật chỉ nằm trong log (đã che nội dung).
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import AppError
from app.observability.logging import get_logger

log = get_logger("api.errors")

_HTTP_DEFAULTS: dict[int, tuple[str, str]] = {
    400: ("bad_request", "Yêu cầu không hợp lệ."),
    401: ("unauthenticated", "Bạn cần đăng nhập để tiếp tục."),
    403: ("forbidden", "Bạn không có quyền thực hiện thao tác này."),
    404: ("not_found", "Không tìm thấy."),
    405: ("method_not_allowed", "Thao tác không được hỗ trợ."),
    413: ("too_large", "Dữ liệu gửi lên quá lớn."),
    415: ("unsupported_media_type", "Định dạng không được hỗ trợ."),
    429: ("too_many_requests", "Quá nhiều yêu cầu. Hãy thử lại sau ít phút."),
}


def error_body(code: str, message: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message}}


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content=error_body(code, message))


async def _app_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return error_response(exc.status_code, exc.code, exc.message)


async def _http_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code, message = _HTTP_DEFAULTS.get(exc.status_code, ("error", "Đã có lỗi xảy ra."))
    return error_response(exc.status_code, code, message)


async def _validation_error(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    # Không trả lại giá trị đầu vào (có thể là nội dung câu hỏi); chỉ nêu vị trí trường lỗi.
    fields = [".".join(str(p) for p in err.get("loc", ())) for err in exc.errors()]
    log.info("request_validation_failed", fields=fields)
    return error_response(400, "invalid_input", "Dữ liệu gửi lên không hợp lệ.")


async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
    log.error(
        "unhandled_error",
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
    )
    return error_response(500, "internal_error", "Đã có lỗi xảy ra. Hãy thử lại sau.")


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(Exception, _unhandled)
