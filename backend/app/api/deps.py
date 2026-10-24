"""Phụ thuộc FastAPI dùng chung: runtime, phiên cơ sở dữ liệu."""

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.orm import Session

from app.config import Settings
from app.runtime import Runtime


def get_runtime(request: Request) -> Runtime:
    runtime: Runtime = request.app.state.runtime
    return runtime


def get_settings_dep(request: Request) -> Settings:
    return get_runtime(request).settings


def get_db(request: Request) -> Iterator[Session]:
    """Một phiên cơ sở dữ liệu cho mỗi yêu cầu; commit khi xử lý xong, rollback khi lỗi."""
    session = get_runtime(request).sessions()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
