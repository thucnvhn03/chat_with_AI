"""T1-08: ma trận xác thực tự sinh từ danh sách route.

- Mọi route (trừ đăng nhập, OIDC, health) trả 401 khi không có phiên.
- Mọi route `/admin/*` trả 403 với vai trò `bd` và `manager`.
Thêm một route mới không có `current_user`/`require_role` làm kiểm thử này đỏ.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import ORIGIN, create_user, login
from tests.security.routes import add_route, all_routes, placeholder_values

pytestmark = pytest.mark.integration

ROUTES = all_routes(create_app(lambda: None))  # type: ignore[arg-type, return-value]


def test_route_list_is_not_empty() -> None:
    paths = {r.path for r in ROUTES}
    assert "/api/v1/documents" in paths and "/api/v1/admin/audit" in paths


@pytest.mark.parametrize(
    "route", [r for r in ROUTES if not r.is_public], ids=lambda r: f"{r.method} {r.path}"
)
def test_every_protected_route_requires_session(client, route) -> None:  # type: ignore[no-untyped-def]
    response = client.request(route.method, route.url(placeholder_values()), json={})
    assert response.status_code == 401, response.text
    assert response.json()["error"]["code"] == "unauthenticated"


@pytest.mark.parametrize("role", ["bd", "manager"])
def test_admin_routes_forbidden_for_non_admin(client, runtime, role: str) -> None:  # type: ignore[no-untyped-def]
    create_user(runtime, "nguoi.dung", role)
    login(client, "nguoi.dung")
    admin_routes = [r for r in ROUTES if r.is_admin]
    assert admin_routes
    for route in admin_routes:
        response = client.request(route.method, route.url(placeholder_values()), json={})
        assert response.status_code == 403, f"{route.method} {route.path}"


def test_unprotected_route_makes_matrix_fail(app, runtime) -> None:  # type: ignore[no-untyped-def]
    """Thêm cố ý một route không kiểm phiên: kiểm tra của ma trận phải phát hiện được."""

    def leaky() -> dict[str, str]:
        return {"secret": "x"}

    add_route(app, "/api/v1/leaky", leaky)
    with TestClient(app, headers={"Origin": ORIGIN}) as c:
        failures = [
            r
            for r in all_routes(app)
            if not r.is_public
            and c.request(r.method, r.url(placeholder_values()), json={}).status_code != 401
        ]
    assert [f.path for f in failures] == ["/api/v1/leaky"]
