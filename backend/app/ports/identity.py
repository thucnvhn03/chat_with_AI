"""Cổng xác thực (P-02).

Vai trò KHÔNG đến từ nhà cung cấp danh tính mà luôn lấy từ `access_grants` của hệ thống
(implement_plan.md mục 6.1), nên cổng này chỉ trả lời câu hỏi "người này là ai".
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: UUID
    login: str
    display_name: str | None


class AuthFailure(StrEnum):
    # Không phân biệt "sai tên đăng nhập" với "sai mật khẩu" (tránh dò tài khoản)
    INVALID_CREDENTIALS = "invalid_credentials"
    LOCKED = "locked"


@dataclass(frozen=True)
class AuthResult:
    user: AuthenticatedUser | None
    failure: AuthFailure | None = None


class IdentityProvider(Protocol):
    """Đăng nhập bằng tài khoản nội bộ (DQ-003 = không có IdP)."""

    def authenticate(self, login: str, password: str, client_addr: str) -> AuthResult: ...

    def set_password(self, login: str, password: str) -> None: ...


@dataclass(frozen=True)
class OidcIdentity:
    subject: str
    email: str | None
    name: str | None


class OidcClient(Protocol):
    """Đăng nhập qua IdP của tổ chức bằng Authorization Code + PKCE (DQ-003 = OIDC)."""

    def authorization_url(self, state: str, nonce: str, code_challenge: str) -> str: ...

    def exchange_code(self, code: str, code_verifier: str, nonce: str) -> OidcIdentity: ...
