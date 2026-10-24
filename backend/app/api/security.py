"""Phụ thuộc bảo mật dùng cho mọi router: phiên, vai trò, CSRF (T1-04).

- Không có cookie phiên → 401 `unauthenticated`; phiên hết hạn/không hợp lệ → 401 `session_expired`.
- Đăng nhập đúng nhưng chưa được cấp quyền hoặc đã bị thu hồi → 403 `no_access`.
- Sai vai trò → 403 `forbidden_role`.
- Yêu cầu thay đổi dữ liệu phải có header `Origin` (hoặc `Referer`) thuộc ALLOWED_ORIGINS.
"""

import uuid
from collections.abc import Callable
from urllib.parse import urlsplit

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_runtime
from app.errors import AppError
from app.modules.access.service import (
    ROLE_BD,
    CurrentUser,
    SessionExpired,
    active_role,
    resolve_session,
)
from app.modules.usage import events

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def check_origin(request: Request) -> None:
    """Bảo vệ CSRF (implement_plan.md mục 10.5): kiểm tra nguồn gốc của yêu cầu thay đổi dữ liệu."""
    if request.method in SAFE_METHODS:
        return
    allowed = get_runtime(request).settings.allowed_origins
    origin = request.headers.get("origin")
    if origin is None:
        referer = request.headers.get("referer")
        if referer:
            parts = urlsplit(referer)
            origin = f"{parts.scheme}://{parts.netloc}"
    if origin is None or origin.rstrip("/") not in allowed:
        raise AppError(403, "csrf_rejected", "Yêu cầu bị từ chối vì không rõ nguồn gốc.")


def _record_denied(request: Request, user_id: uuid.UUID, reason: str) -> None:
    # Ghi bằng phiên riêng: phiên của yêu cầu sẽ bị rollback khi ném lỗi.
    runtime = get_runtime(request)
    with runtime.sessions() as db, db.begin():
        events.record(db, user_id, events.ACCESS_DENIED, reason=reason)


def current_user(request: Request, db: Session = Depends(get_db, scope="function")) -> CurrentUser:
    runtime = get_runtime(request)
    settings = runtime.settings
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise AppError(401, "unauthenticated", "Bạn cần đăng nhập để tiếp tục.")
    try:
        user = resolve_session(db, token, settings.session_idle_hours)
    except SessionExpired:
        db.commit()  # lưu việc xóa phiên hết hạn
        raise AppError(
            401, "session_expired", "Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại."
        ) from None
    role = active_role(db, user.id)
    if role is None:
        _record_denied(request, user.id, "no_access")
        raise AppError(403, "no_access", "Tài khoản của bạn chưa được cấp quyền sử dụng hệ thống.")
    if role == ROLE_BD:
        # Người dùng hoạt động (US-022) chỉ tính nhân sự BD, không tính quản lý/quản trị xem báo cáo
        events.record_session_started_once_per_day(db, user.id)
    current = CurrentUser(user.id, user.login, user.display_name, role)
    request.state.user = current
    return current


def require_role(*roles: str) -> Callable[..., CurrentUser]:
    def dependency(request: Request, user: CurrentUser = Depends(current_user)) -> CurrentUser:
        if user.role not in roles:
            _record_denied(request, user.id, "forbidden_role")
            raise AppError(403, "forbidden_role", "Vai trò của bạn không được dùng chức năng này.")
        return user

    return dependency
