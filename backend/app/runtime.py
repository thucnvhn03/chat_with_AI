"""Các phụ thuộc đã khởi tạo của tiến trình (cấu hình, cơ sở dữ liệu, cài đặt cổng).

Chỉ tham chiếu kiểu của cổng (`app.ports`), không tham chiếu adapter: lớp API và mô-đun nghiệp vụ
nhận `Runtime` mà không biết adapter cụ thể nào đang chạy. Adapter được chọn ở `app/container.py`.
"""

from dataclasses import dataclass, field

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  (nạp đủ model trước khi dùng ORM)
from app.config import Settings
from app.observability.health import HealthCheck
from app.ports.ai import AnswerGenerator, EmbeddingProvider
from app.ports.identity import IdentityProvider, OidcClient
from app.ports.storage import FileStore


@dataclass
class Runtime:
    settings: Settings
    engine: Engine
    sessions: sessionmaker[Session]
    file_store: FileStore
    embedder: EmbeddingProvider
    answer_generator: AnswerGenerator
    identity: IdentityProvider
    oidc: OidcClient | None = None
    health_checks: dict[str, HealthCheck] = field(default_factory=dict)
