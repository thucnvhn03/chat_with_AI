"""Cấu hình ứng dụng, đọc từ biến môi trường.

Mọi ngưỡng còn [TBD] trong BRD/PRD là một trường ở đây, kèm giá trị mặc định tạm thời CHỈ để phát
triển (implement_plan.md mục 10.3). Không viết cứng ngưỡng ở nơi khác trong mã.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore", case_sensitive=False)

    # ------------------------------------------------------------ Môi trường và kết nối
    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://chat:chat_dev_password@localhost:5432/chat"

    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str = "documents"
    s3_region: str = "us-east-1"
    # Mã hóa phía máy chủ của kho đối tượng (OQ-005). "" = tắt (RustFS/MinIO cục bộ không cấu hình KMS)
    s3_server_side_encryption: str = ""
    # Tạo bucket khi khởi động nếu chưa có (chỉ dùng ở môi trường phát triển)
    s3_create_bucket: bool = True

    # ------------------------------------------------------------ Xác thực, phiên (DQ-003)
    auth_mode: Literal["local", "oidc"] = "local"
    session_idle_hours: float = 8
    session_cookie_name: str = "cwd_session"
    cookie_secure: bool = True
    # Origin được phép gửi yêu cầu thay đổi dữ liệu (bảo vệ CSRF, mục 10.5)
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    login_max_failures: int = 5
    login_failure_window_minutes: int = 15

    oidc_issuer: str | None = None
    oidc_client_id: str | None = None
    oidc_client_secret: str | None = None
    oidc_redirect_uri: str | None = None
    oidc_scopes: str = "openid email profile"
    # Đường dẫn giao diện sau khi đăng nhập OIDC xong
    oidc_post_login_redirect: str = "/"

    # ------------------------------------------------------------ Tải lên (OQ-004)
    max_file_bytes: int = 20 * 1024 * 1024
    max_docs_per_user: int = 50
    min_text_chars: int = 20

    # ------------------------------------------------------------ Chunk, embedding, truy xuất
    chunk_tokens: int = 500
    chunk_overlap: int = 80
    embed_batch: int = 32
    embedding_provider: Literal["local", "hash"] = "local"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024
    top_k: int = 8
    # 0 = không giới hạn số chunk mỗi tài liệu
    max_chunks_per_doc: int = 4
    # [TBD: AQ-002] Hiệu chỉnh bằng bộ đánh giá. Điểm = 1 - khoảng cách cosine.
    min_relevance_score: float = 0.35
    hnsw_ef_search: int = 100

    # ------------------------------------------------------------ Hỏi đáp
    answer_provider: Literal["claude", "fake"] = "claude"
    answer_model: str = "claude-opus-5-5"
    answer_effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"
    answer_max_tokens: int = 16000
    answer_timeout_s: float = 60
    answer_max_retries: int = 2
    # Chuyển mô hình dự phòng phía máy chủ khi bị từ chối (beta server-side-fallback-2026-07-01)
    answer_server_fallback: bool = True
    anthropic_api_key: str | None = None
    max_question_chars: int = 2000
    history_turns: int = 4
    # [TBD: PQ-004] Hội thoại (câu hỏi, câu trả lời, trích dẫn, đánh giá) không hoạt động quá số ngày này
    # bị xóa định kỳ. 60 ngày đủ phủ báo cáo 8 tuần (xóa tin nhắn kéo theo xóa đánh giá). 0 = không xóa.
    message_retention_days: int = 60

    # ------------------------------------------------------------ Xóa, kiểm toán (OQ-012)
    purge_sla_hours: float = 24
    audit_retention_days: int = 365

    # ------------------------------------------------------------ Worker
    job_max_attempts: int = 3
    worker_concurrency: int = 2
    job_retry_base_s: float = 5
    worker_poll_interval_s: float = 1
    worker_metrics_port: int = 9100
    maintenance_interval_s: float = 300

    # ------------------------------------------------------------ Giao diện, giám sát
    poll_interval_s: float = 3
    # /health/ready báo lỗi khi việc cũ nhất trong hàng đợi chờ quá lâu
    queue_max_age_s: float = 600


@lru_cache
def get_settings() -> Settings:
    return Settings()
