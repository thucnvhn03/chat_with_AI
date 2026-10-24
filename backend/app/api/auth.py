"""IF-01: đăng nhập, đăng xuất, thông tin phiên (US-017).

- `POST /auth/login`: tài khoản nội bộ (AUTH_MODE=local).
- `GET /auth/oidc/login`, `GET /auth/oidc/callback`: OIDC Authorization Code + PKCE (AUTH_MODE=oidc).
- `GET /auth/me`: người dùng, vai trò, và các giới hạn giao diện cần biết (đọc từ cấu hình).
"""

import base64
import hashlib
import secrets
import uuid

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_runtime
from app.api.security import current_user
from app.config import Settings
from app.errors import AppError
from app.modules.access.service import (
    ROLE_BD,
    CurrentUser,
    active_role,
    create_session,
    end_session,
    find_or_create_user,
)
from app.modules.usage import events
from app.observability.logging import get_logger
from app.ports.identity import AuthFailure

router = APIRouter(prefix="/auth", tags=["auth"])
log = get_logger("api.auth")

OIDC_STATE_COOKIE = "cwd_oidc"


class LoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=1, max_length=500)


class UserOut(BaseModel):
    id: uuid.UUID
    login: str
    display_name: str | None


class ClientConfig(BaseModel):
    """Giới hạn giao diện cần hiển thị/kiểm tra sớm. Quyết định cuối vẫn ở backend."""

    max_file_bytes: int
    max_docs_per_user: int
    max_question_chars: int
    poll_interval_s: float
    purge_sla_hours: float
    auth_mode: str


class MeOut(BaseModel):
    user: UserOut
    role: str
    config: ClientConfig


def client_config(settings: Settings) -> ClientConfig:
    return ClientConfig(
        max_file_bytes=settings.max_file_bytes,
        max_docs_per_user=settings.max_docs_per_user,
        max_question_chars=settings.max_question_chars,
        poll_interval_s=settings.poll_interval_s,
        purge_sla_hours=settings.purge_sla_hours,
        auth_mode=settings.auth_mode,
    )


def _set_session_cookie(response: Response, settings: Settings, token: str) -> None:
    response.set_cookie(
        settings.session_cookie_name,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def _start_session(db: Session, response: Response, settings: Settings, user_id: uuid.UUID) -> str:
    role = active_role(db, user_id)
    if role is None:
        raise AppError(403, "no_access", "Tài khoản của bạn chưa được cấp quyền sử dụng hệ thống.")
    _set_session_cookie(response, settings, create_session(db, user_id))
    if role == ROLE_BD:
        events.record_session_started_once_per_day(db, user_id)
    return role


@router.post("/login", response_model=MeOut)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db, scope="function"),
) -> MeOut:
    runtime = get_runtime(request)
    settings = runtime.settings
    if settings.auth_mode != "local":
        raise AppError(404, "not_found", "Không tìm thấy.")
    client_addr = request.client.host if request.client else "unknown"
    result = runtime.identity.authenticate(body.login, body.password, client_addr)
    if result.user is None:
        if result.failure == AuthFailure.LOCKED:
            raise AppError(
                429,
                "login_locked",
                "Đăng nhập sai quá nhiều lần. Hãy thử lại sau ít phút.",
            )
        # Không phân biệt sai tên đăng nhập với sai mật khẩu
        raise AppError(401, "invalid_credentials", "Tên đăng nhập hoặc mật khẩu không đúng.")
    try:
        role = _start_session(db, response, settings, result.user.user_id)
    except AppError:
        with runtime.sessions() as other, other.begin():
            events.record(other, result.user.user_id, events.ACCESS_DENIED, reason="no_access")
        raise
    user = result.user
    return MeOut(
        user=UserOut(id=user.user_id, login=user.login, display_name=user.display_name),
        role=role,
        config=client_config(settings),
    )


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db, scope="function"),
    _user: CurrentUser = Depends(current_user),
) -> Response:
    settings = get_runtime(request).settings
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        end_session(db, token)
    response = Response(status_code=204)
    response.delete_cookie(settings.session_cookie_name, path="/")
    return response


@router.get("/me", response_model=MeOut)
def me(request: Request, user: CurrentUser = Depends(current_user)) -> MeOut:
    return MeOut(
        user=UserOut(id=user.id, login=user.login, display_name=user.display_name),
        role=user.role,
        config=client_config(get_runtime(request).settings),
    )


# ------------------------------------------------------------------ OIDC (DQ-003 = OIDC)


def _pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


@router.get("/oidc/login")
def oidc_login(request: Request) -> RedirectResponse:
    runtime = get_runtime(request)
    if runtime.settings.auth_mode != "oidc" or runtime.oidc is None:
        raise AppError(404, "not_found", "Không tìm thấy.")
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    verifier = secrets.token_urlsafe(48)
    url = runtime.oidc.authorization_url(state, nonce, _pkce_challenge(verifier))
    response = RedirectResponse(url, status_code=302)
    response.set_cookie(
        OIDC_STATE_COOKIE,
        f"{state}.{nonce}.{verifier}",
        httponly=True,
        secure=runtime.settings.cookie_secure,
        samesite="lax",
        max_age=600,
        path="/api/v1/auth/oidc",
    )
    return response


@router.get("/oidc/callback")
def oidc_callback(
    request: Request,
    code: str = "",
    state: str = "",
    db: Session = Depends(get_db, scope="function"),
) -> RedirectResponse:
    runtime = get_runtime(request)
    settings = runtime.settings
    if settings.auth_mode != "oidc" or runtime.oidc is None:
        raise AppError(404, "not_found", "Không tìm thấy.")
    stored = request.cookies.get(OIDC_STATE_COOKIE, "")
    parts = stored.split(".")
    if len(parts) != 3 or not code or not secrets.compare_digest(parts[0], state):
        raise AppError(400, "oidc_state_mismatch", "Phiên đăng nhập không hợp lệ. Hãy thử lại.")
    _, nonce, verifier = parts
    try:
        identity = runtime.oidc.exchange_code(code, verifier, nonce)
    except Exception as exc:
        log.warning("oidc_exchange_failed", error_type=type(exc).__name__)
        raise AppError(
            401, "oidc_failed", "Không đăng nhập được qua hệ thống của tổ chức."
        ) from exc

    # Ánh xạ email (ưu tiên) hoặc sub của IdP sang users.login. Vai trò lấy từ access_grants.
    user = find_or_create_user(db, identity.email or identity.subject, identity.name)
    target = settings.oidc_post_login_redirect
    response = RedirectResponse(target, status_code=302)
    response.delete_cookie(OIDC_STATE_COOKIE, path="/api/v1/auth/oidc")
    if active_role(db, user.id) is None:
        events.record(db, user.id, events.ACCESS_DENIED, reason="no_access")
        # Giao diện S-01 hiển thị trạng thái "không có quyền" theo tham số này
        response.headers["location"] = "/login?error=no_access"
        return response
    _start_session(db, response, settings, user.id)
    return response
