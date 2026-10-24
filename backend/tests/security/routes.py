"""Liệt kê mọi route của ứng dụng để kiểm thử bảo mật tự mở rộng khi thêm route mới."""

import re
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.routing import APIRoute

# Route công khai (không cần phiên). Thêm route vào đây phải có lý do rõ ràng.
PUBLIC_PATHS = (
    re.compile(r"^/api/v1/auth/login$"),
    re.compile(r"^/api/v1/auth/oidc/.*"),
    re.compile(r"^/health/.*"),
)


@dataclass(frozen=True)
class RouteInfo:
    method: str
    path: str
    params: tuple[str, ...]

    @property
    def is_public(self) -> bool:
        return any(p.match(self.path) for p in PUBLIC_PATHS)

    @property
    def is_admin(self) -> bool:
        return self.path.startswith("/api/v1/admin/")

    def url(self, values: dict[str, str]) -> str:
        url = self.path
        for name in self.params:
            url = url.replace("{" + name + "}", values[name])
        return url


def all_routes(app: FastAPI) -> list[RouteInfo]:
    """Mọi cặp (phương thức, đường dẫn) trong OpenAPI của ứng dụng (sinh lại mỗi lần gọi)."""
    app.openapi_schema = None
    result: list[RouteInfo] = []
    for path, operations in app.openapi()["paths"].items():
        params = tuple(re.findall(r"{(\w+)}", path))
        for method in sorted(operations):
            if method.upper() in {"HEAD", "OPTIONS"}:
                continue
            result.append(RouteInfo(method.upper(), path, params))
    return result


def add_route(app: FastAPI, path: str, endpoint: object, method: str = "GET") -> None:
    """Thêm route trực tiếp vào ứng dụng (dùng để chứng minh kiểm thử phát hiện route thiếu bảo vệ)."""
    app.router.routes.append(APIRoute(path, endpoint, methods=[method]))  # type: ignore[arg-type]


def placeholder_values() -> dict[str, str]:
    return {
        "document_id": "00000000-0000-0000-0000-000000000001",
        "conversation_id": "00000000-0000-0000-0000-000000000002",
        "message_id": "00000000-0000-0000-0000-000000000003",
        "user_id": "00000000-0000-0000-0000-000000000004",
        "page": "1",
    }
