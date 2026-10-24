"""Điểm vào của ứng dụng FastAPI.

`create_app(runtime)` cho phép kiểm thử truyền runtime với adapter giả. Khi chạy bằng uvicorn
(`app.main:app`), runtime được dựng từ biến môi trường ở `app/container.py` trong lúc khởi động.
"""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.errors import install_error_handlers
from app.api.router import api_router, health_router
from app.config import get_settings
from app.observability.logging import configure_logging
from app.observability.middleware import RequestContextMiddleware
from app.runtime import Runtime


def create_app(runtime_factory: Callable[[], Runtime] | None = None) -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if runtime_factory is not None:
            app.state.runtime = runtime_factory()
        else:
            from app.container import build_runtime  # adapter chỉ được nạp ở gốc ứng dụng

            app.state.runtime = build_runtime(settings, role="api")
        yield
        app.state.runtime.engine.dispose()

    app = FastAPI(
        title="Chat với tài liệu",
        version="0.1.0",
        lifespan=lifespan,
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url=None,
    )
    app.add_middleware(RequestContextMiddleware)
    install_error_handlers(app)
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")
    # Số liệu Prometheus: chỉ dành cho mạng nội bộ; frontend chỉ chuyển tiếp /api nên trình duyệt
    # không tới được đường dẫn này qua proxy.
    app.mount("/metrics", make_asgi_app())
    return app


app = create_app()
