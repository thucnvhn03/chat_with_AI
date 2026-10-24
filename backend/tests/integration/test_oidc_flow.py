"""T1-03: đăng nhập OIDC (Authorization Code + PKCE) qua endpoint, với IdP giả lập.

Vai trò KHÔNG lấy từ IdP: người đăng nhập đúng qua IdP nhưng chưa có access_grants nhận no_access.
"""

import base64
import hashlib
from urllib.parse import parse_qs, urlsplit

import pytest

from app.ports.identity import OidcIdentity
from tests.conftest import create_user

pytestmark = pytest.mark.integration


class FakeOidc:
    def __init__(self, identity: OidcIdentity) -> None:
        self.identity = identity
        self.challenge = ""
        self.verifier = ""

    def authorization_url(self, state: str, nonce: str, code_challenge: str) -> str:
        self.challenge = code_challenge
        return f"https://idp.test/authorize?state={state}&nonce={nonce}"

    def exchange_code(self, code: str, code_verifier: str, nonce: str) -> OidcIdentity:
        self.verifier = code_verifier
        return self.identity


@pytest.fixture
def oidc(runtime):  # type: ignore[no-untyped-def]
    fake = FakeOidc(OidcIdentity(subject="sub-1", email="an.oidc@example.test", name="An OIDC"))
    runtime.oidc = fake
    runtime.settings = runtime.settings.model_copy(update={"auth_mode": "oidc"})
    return fake


def _login(client) -> str:  # type: ignore[no-untyped-def]
    start = client.get("/api/v1/auth/oidc/login", follow_redirects=False)
    assert start.status_code == 302
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    callback = client.get(
        f"/api/v1/auth/oidc/callback?code=abc&state={state}", follow_redirects=False
    )
    assert callback.status_code == 302
    return callback.headers["location"]


def test_oidc_login_with_grant_creates_session(client, runtime, oidc) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "an.oidc@example.test", "bd")
    assert _login(client) == "/"
    # PKCE: verifier gửi lúc đổi mã khớp challenge đã gửi lúc chuyển hướng
    digest = hashlib.sha256(oidc.verifier.encode()).digest()
    assert base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == oidc.challenge
    me = client.get("/api/v1/auth/me").json()
    assert me["user"]["login"] == "an.oidc@example.test" and me["role"] == "bd"


def test_oidc_login_without_grant_is_no_access(client, runtime, oidc) -> None:  # type: ignore[no-untyped-def]
    assert _login(client) == "/login?error=no_access"
    assert client.get("/api/v1/auth/me").status_code == 401
    # Người dùng được tạo (khớp theo email) nhưng không có quyền
    with runtime.sessions() as db:
        from sqlalchemy import select

        from app.modules.access.models import User

        assert db.scalar(select(User).where(User.login == "an.oidc@example.test")) is not None


def test_oidc_state_mismatch_rejected(client, oidc) -> None:  # type: ignore[no-untyped-def]
    client.get("/api/v1/auth/oidc/login", follow_redirects=False)
    response = client.get(
        "/api/v1/auth/oidc/callback?code=abc&state=gia-mao", follow_redirects=False
    )
    assert response.status_code == 400


def test_local_login_disabled_in_oidc_mode(client, oidc) -> None:  # type: ignore[no-untyped-def]
    assert (
        client.post("/api/v1/auth/login", json={"login": "a", "password": "b"}).status_code == 404
    )
