"""GET /health/live, GET /health/ready (US-021). Không cần đăng nhập, không trả thông tin nhạy cảm."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.deps import get_runtime
from app.observability.health import run_checks

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def health_live() -> dict[str, str]:
    """Tiến trình còn sống. Không kiểm tra các thành phần phụ thuộc (việc của /health/ready)."""
    return {"status": "ok"}


@router.get("/ready")
def health_ready(request: Request) -> JSONResponse:
    ok, components = run_checks(get_runtime(request).health_checks)
    return JSONResponse(
        status_code=200 if ok else 503,
        content={"status": "ok" if ok else "unavailable", "components": components},
    )
