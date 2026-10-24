"""Lỗi nghiệp vụ dùng chung giữa các mô-đun và lớp API.

Mô-đun nghiệp vụ ném `AppError` với mã ổn định; lớp API (`app/api/errors.py`) chuyển nó thành
`{"error": {"code", "message"}}`. Thông điệp dành cho người dùng, không chứa chi tiết kỹ thuật.
"""


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.message = message


def not_found(code: str = "not_found", message: str = "Không tìm thấy.") -> AppError:
    # Dùng cả khi tài liệu tồn tại nhưng ngoài phạm vi người dùng: không tiết lộ sự tồn tại.
    return AppError(404, code, message)


def bad_request(code: str, message: str) -> AppError:
    return AppError(400, code, message)


def forbidden(code: str, message: str) -> AppError:
    return AppError(403, code, message)


def conflict(code: str, message: str) -> AppError:
    return AppError(409, code, message)
