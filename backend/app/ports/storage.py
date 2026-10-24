"""Cổng lưu trữ tệp (P-03). Trình duyệt không bao giờ nhận đường dẫn trực tiếp tới kho."""

from typing import BinaryIO, Protocol


class FileStore(Protocol):
    def put(self, key: str, data: BinaryIO) -> None: ...

    def get(self, key: str) -> bytes: ...

    def delete(self, key: str) -> None:
        """Không báo lỗi nếu khóa không còn (xóa làm lại được nhiều lần)."""
        ...

    def exists(self, key: str) -> bool: ...

    def check(self) -> None:
        """Ném ngoại lệ nếu kho không truy cập được (dùng cho /health/ready)."""
        ...
