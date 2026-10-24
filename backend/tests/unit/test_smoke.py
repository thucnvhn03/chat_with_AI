"""Kiểm thử mẫu để chứng minh khung kiểm thử chạy được (T0-01)."""

import importlib

import pytest

PACKAGES = [
    "app.api",
    "app.modules.access",
    "app.modules.documents",
    "app.modules.ingestion",
    "app.modules.retrieval",
    "app.modules.qa",
    "app.modules.conversation",
    "app.modules.sources",
    "app.modules.usage",
    "app.modules.audit",
    "app.modules.jobs",
    "app.ports",
    "app.adapters",
    "app.worker",
    "app.observability",
]


@pytest.mark.parametrize("name", PACKAGES)
def test_package_is_importable(name: str) -> None:
    assert importlib.import_module(name).__name__ == name


def test_api_process_loads_every_model() -> None:
    """Tiến trình API (chỉ import app.main) phải phân giải được mọi khóa ngoại giữa các bảng.

    Hồi quy: trước đây model `Chunk` chỉ được nạp ở worker nên lưu câu trả lời ở API lỗi.
    Chạy trong tiến trình mới vì bộ kiểm thử đã nạp sẵn mọi model.
    """
    import subprocess
    import sys

    code = "import app.main; from sqlalchemy.orm import configure_mappers; configure_mappers()"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-2000:]
