"""T1-02, T1-04, T1-05: tài khoản nội bộ, phiên, require_role, CSRF, quản lý quyền, create-admin."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select, update

from app.db import transaction
from app.modules.access.models import UserSession
from app.modules.usage.models import UsageEvent
from app.ports.identity import AuthFailure
from tests.conftest import TEST_PASSWORD, create_user, login

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------- adapter tài khoản nội bộ (T1-02)


def test_local_identity_right_and_wrong_password(runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "an", "bd")
    ok = runtime.identity.authenticate("an", TEST_PASSWORD, "10.0.0.1")
    assert ok.user is not None and ok.user.login == "an"
    wrong = runtime.identity.authenticate("an", "sai-mat-khau", "10.0.0.1")
    unknown = runtime.identity.authenticate("khong-co", "sai-mat-khau", "10.0.0.1")
    assert wrong.user is None and unknown.user is None
    # Không phân biệt sai tên với sai mật khẩu
    assert wrong.failure == unknown.failure == AuthFailure.INVALID_CREDENTIALS


def test_local_identity_locks_after_too_many_failures(runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "binh", "bd")
    for _ in range(5):
        assert (
            runtime.identity.authenticate("binh", "sai", "10.0.0.2").failure
            == AuthFailure.INVALID_CREDENTIALS
        )
    locked = runtime.identity.authenticate("binh", TEST_PASSWORD, "10.0.0.2")
    assert locked.user is None and locked.failure == AuthFailure.LOCKED
    # Người khác từ địa chỉ khác không bị ảnh hưởng
    create_user(runtime, "chi", "bd")
    assert runtime.identity.authenticate("chi", TEST_PASSWORD, "10.0.0.3").user is not None


def test_password_hash_is_argon2id(runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "dung", "bd")
    with runtime.sessions() as db:
        from app.modules.access.models import User

        stored = db.scalar(select(User.password_hash).where(User.login == "dung"))
    assert stored.startswith("$argon2id$") and TEST_PASSWORD not in stored


# ---------------------------------------------------------------- endpoint xác thực (T1-04)


def test_login_me_logout(client, runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "an", "bd")
    response = client.post("/api/v1/auth/login", json={"login": "an", "password": TEST_PASSWORD})
    assert response.status_code == 200
    assert response.json()["role"] == "bd"
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie
    me = client.get("/api/v1/auth/me").json()
    assert me["user"]["login"] == "an" and me["config"]["max_question_chars"] > 0
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


def test_login_wrong_password_is_generic(client, runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "an", "bd")
    wrong = client.post("/api/v1/auth/login", json={"login": "an", "password": "x"})
    unknown = client.post("/api/v1/auth/login", json={"login": "ai-do", "password": "x"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_login_without_grant_is_no_access(client, runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "khach", None)
    response = client.post("/api/v1/auth/login", json={"login": "khach", "password": TEST_PASSWORD})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "no_access"
    assert "set-cookie" not in response.headers


def test_no_session_is_401(client) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/api/v1/documents")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


def test_expired_session_is_session_expired(client, runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "an", "bd")
    login(client, "an")
    stale = datetime.now(UTC) - timedelta(hours=runtime.settings.session_idle_hours + 1)
    with transaction(runtime.sessions) as db:
        db.execute(update(UserSession).values(last_seen_at=stale))
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "session_expired"


def test_revoked_user_loses_access_on_next_request(client, make_client, runtime) -> None:  # type: ignore[no-untyped-def]
    """AC-014: người bị thu hồi quyền mất truy cập ở yêu cầu kế tiếp."""
    create_user(runtime, "admin", "security_admin")
    bd_id = create_user(runtime, "an", "bd")
    login(client, "an")
    assert client.get("/api/v1/documents").status_code == 200

    admin = make_client()
    login(admin, "admin")
    assert admin.delete(f"/api/v1/admin/access/{bd_id}").status_code == 204

    response = client.get("/api/v1/documents")
    assert response.status_code in (401, 403)
    again = client.post("/api/v1/auth/login", json={"login": "an", "password": TEST_PASSWORD})
    assert again.status_code == 403 and again.json()["error"]["code"] == "no_access"


def test_wrong_role_is_forbidden_role_and_records_access_denied(client, runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "an", "bd")
    login(client, "an")
    response = client.get("/api/v1/admin/access")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_role"
    with runtime.sessions() as db:
        denied = db.scalar(
            select(func.count()).select_from(UsageEvent).where(UsageEvent.kind == "access_denied")
        )
    assert denied == 1


def test_post_without_valid_origin_is_rejected(app, runtime) -> None:  # type: ignore[no-untyped-def]
    from fastapi.testclient import TestClient

    create_user(runtime, "an", "bd")
    with TestClient(app) as bare:
        body = {"login": "an", "password": TEST_PASSWORD}
        assert bare.post("/api/v1/auth/login", json=body).status_code == 403
        evil = bare.post(
            "/api/v1/auth/login", json=body, headers={"Origin": "https://evil.example"}
        )
        assert evil.status_code == 403 and evil.json()["error"]["code"] == "csrf_rejected"
        ok = bare.post("/api/v1/auth/login", json=body, headers={"Origin": "http://localhost:5173"})
        assert ok.status_code == 200


def test_session_started_once_per_day(client, runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "an", "bd")
    login(client, "an")
    client.get("/api/v1/auth/me")
    login(client, "an")
    with runtime.sessions() as db:
        count = db.scalar(
            select(func.count()).select_from(UsageEvent).where(UsageEvent.kind == "session_started")
        )
    assert count == 1


# ---------------------------------------------------------------- quản lý quyền (T1-05)


def test_admin_grant_list_revoke(client, runtime) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "admin", "security_admin")
    login(client, "admin")
    created = client.post("/api/v1/admin/access", json={"login": "moi.nguoi", "role": "manager"})
    assert created.status_code == 201
    body = created.json()
    assert body["login"] == "moi.nguoi" and body["role"] == "manager" and body["status"] == "active"

    listing = client.get("/api/v1/admin/access").json()
    assert {g["login"] for g in listing} == {"admin", "moi.nguoi"}

    assert client.delete(f"/api/v1/admin/access/{body['user_id']}").status_code == 204
    revoked = next(
        g for g in client.get("/api/v1/admin/access").json() if g["login"] == "moi.nguoi"
    )
    assert revoked["status"] == "revoked" and revoked["revoked_at"] is not None

    assert (
        client.post("/api/v1/admin/access", json={"login": "x", "role": "root"}).status_code == 400
    )


def test_admin_cannot_revoke_self(client, runtime) -> None:  # type: ignore[no-untyped-def]
    admin_id = create_user(runtime, "admin", "security_admin")
    login(client, "admin")
    assert client.delete(f"/api/v1/admin/access/{admin_id}").status_code == 409


@pytest.mark.parametrize("role", ["bd", "manager"])
def test_admin_endpoints_forbidden_for_other_roles(client, runtime, role: str) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "nguoi", role)
    login(client, "nguoi")
    assert client.get("/api/v1/admin/access").status_code == 403
    assert client.post("/api/v1/admin/access", json={"login": "x", "role": "bd"}).status_code == 403


def test_cli_create_admin_on_empty_database(runtime, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from app import cli

    monkeypatch.setenv("INITIAL_PASSWORD", "mat-khau-quan-tri-dau-tien")
    monkeypatch.setattr(cli, "get_settings", lambda: runtime.settings)
    cli.main(["create-admin", "quan.tri"])
    result = runtime.identity.authenticate("quan.tri", "mat-khau-quan-tri-dau-tien", "127.0.0.1")
    assert result.user is not None
    with runtime.sessions() as db:
        from app.modules.access.service import active_role

        assert active_role(db, result.user.user_id) == "security_admin"
