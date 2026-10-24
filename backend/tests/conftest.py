"""Fixture dùng chung (T0-10).

Kiểm thử tích hợp chạy với PostgreSQL (pgvector) và kho S3 THẬT:
- Nếu đặt TEST_DATABASE_URL / TEST_S3_ENDPOINT_URL (ví dụ trỏ vào Docker Compose cục bộ), dùng chúng —
  mỗi phiên kiểm thử tạo một cơ sở dữ liệu và một bucket riêng rồi xóa đi khi xong.
- Nếu không, khởi động container bằng testcontainers (cách CI dùng).
Migration Alembic chạy một lần đầu phiên (`upgrade head`).
"""

import os

# Cấu hình phải đặt trước khi import ứng dụng (Settings được đọc một lần và lưu đệm)
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("EMBEDDING_PROVIDER", "hash")
os.environ.setdefault("ANSWER_PROVIDER", "fake")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("S3_CREATE_BUCKET", "true")
os.environ.setdefault("LOG_LEVEL", "WARNING")

import uuid
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.adapters.fake_llm import FakeAnswerGenerator
from app.adapters.hash_embedding import HashEmbeddingProvider
from app.adapters.local_identity import LocalIdentityProvider
from app.adapters.s3_file_store import S3FileStore
from app.config import Settings, get_settings
from app.container import default_health_checks
from app.db import make_engine, make_session_factory, transaction
from app.main import create_app
from app.modules.access.models import AccessGrant
from app.modules.access.service import find_or_create_user
from app.runtime import Runtime
from app.worker.run import Worker, default_handlers

ORIGIN = "http://localhost:5173"
TEST_PASSWORD = "mat-khau-kiem-thu-123"
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TABLES = [
    "feedback",
    "citations",
    "messages",
    "conversations",
    "audit_records",
    "usage_events",
    "document_acl",
    "chunks",
    "jobs",
    "documents",
    "sessions",
    "login_failures",
    "access_grants",
    "users",
]


# ------------------------------------------------------------------ hạ tầng (mỗi phiên kiểm thử)


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    base = os.environ.get("TEST_DATABASE_URL")
    if base:
        name = f"cwd_test_{uuid.uuid4().hex[:8]}"
        admin = create_engine(base, isolation_level="AUTOCOMMIT")
        with admin.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{name}"'))
        url = make_url(base).set(database=name).render_as_string(hide_password=False)
        try:
            yield url
        finally:
            with admin.connect() as conn:
                conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
            admin.dispose()
        return

    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("pgvector/pgvector:pg16", driver="psycopg") as pg:
        yield pg.get_connection_url()


def alembic_config(url: str) -> Config:
    cfg = Config(os.path.join(BACKEND_DIR, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "alembic"))
    cfg.attributes["database_url"] = url
    cfg.attributes["configure_logger"] = False
    return cfg


@pytest.fixture(scope="session")
def migrated_url(database_url: str) -> str:
    command.upgrade(alembic_config(database_url), "head")
    return database_url


@dataclass
class S3Info:
    endpoint: str
    access_key: str
    secret_key: str


@pytest.fixture(scope="session")
def s3_info() -> Iterator[S3Info]:
    endpoint = os.environ.get("TEST_S3_ENDPOINT_URL")
    if endpoint:
        yield S3Info(
            endpoint,
            os.environ.get("TEST_S3_ACCESS_KEY", "chat_s3"),
            os.environ.get("TEST_S3_SECRET_KEY", "chat_s3_dev_password"),
        )
        return

    from testcontainers.core.container import DockerContainer
    from testcontainers.core.waiting_utils import wait_for_logs

    access, secret = "testkey123", "testsecret12345"
    container = (
        DockerContainer("rustfs/rustfs:1.0.3")
        .with_env("RUSTFS_ACCESS_KEY", access)
        .with_env("RUSTFS_SECRET_KEY", secret)
        .with_exposed_ports(9000)
    )
    with container:
        wait_for_logs(container, "Starting", timeout=60)
        host = container.get_container_host_ip()
        port = container.get_exposed_port(9000)
        yield S3Info(f"http://{host}:{port}", access, secret)


@pytest.fixture(scope="session")
def bucket_name() -> str:
    return f"cwd-test-{uuid.uuid4().hex[:8]}"


# ------------------------------------------------------------------ runtime và client (mỗi kiểm thử)


def make_settings(url: str, s3: S3Info, bucket: str, **overrides: object) -> Settings:
    base = get_settings().model_copy(
        update={
            "database_url": url,
            "s3_endpoint_url": s3.endpoint,
            "s3_access_key": s3.access_key,
            "s3_secret_key": s3.secret_key,
            "s3_bucket": bucket,
            "cookie_secure": False,
            "min_relevance_score": 0.2,
            "job_retry_base_s": 0,
            "chunk_tokens": 60,
            "chunk_overlap": 10,
        }
    )
    return base.model_copy(update=overrides)


@pytest.fixture(scope="session")
def _engine(migrated_url: str):  # type: ignore[no-untyped-def]
    engine = make_engine(migrated_url)
    yield engine
    engine.dispose()


@pytest.fixture
def runtime(_engine, migrated_url: str, s3_info: S3Info, bucket_name: str) -> Iterator[Runtime]:  # type: ignore[no-untyped-def]
    with _engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(TABLES)} RESTART IDENTITY CASCADE"))
    settings = make_settings(migrated_url, s3_info, bucket_name)
    sessions = make_session_factory(_engine)
    store = S3FileStore(
        settings.s3_bucket,
        settings.s3_endpoint_url,
        settings.s3_access_key,
        settings.s3_secret_key,
        settings.s3_region,
    )
    store.ensure_bucket()
    yield Runtime(
        settings=settings,
        engine=_engine,
        sessions=sessions,
        file_store=store,
        embedder=HashEmbeddingProvider(settings.embedding_dim),
        answer_generator=FakeAnswerGenerator(),
        identity=LocalIdentityProvider(sessions, 5, 15),
        health_checks=default_health_checks(settings, sessions, store),
    )


@pytest.fixture
def app(runtime: Runtime):  # type: ignore[no-untyped-def]
    return create_app(lambda: runtime)


@pytest.fixture
def client(app) -> Iterator[TestClient]:  # type: ignore[no-untyped-def]
    with TestClient(app, headers={"Origin": ORIGIN}) as c:
        yield c


@pytest.fixture
def worker(runtime: Runtime) -> Worker:
    return Worker(runtime, default_handlers())


def create_user(
    runtime: Runtime, login: str, role: str | None, password: str = TEST_PASSWORD
) -> uuid.UUID:
    with transaction(runtime.sessions) as db:
        user = find_or_create_user(db, login)
        if role is not None:
            db.add(AccessGrant(user_id=user.id, role=role, status="active"))
        user_id = user.id
    runtime.identity.set_password(login, password)
    return user_id


def login(client: TestClient, login_name: str, password: str = TEST_PASSWORD) -> None:
    response = client.post("/api/v1/auth/login", json={"login": login_name, "password": password})
    assert response.status_code == 200, response.text


@pytest.fixture
def make_client(app):  # type: ignore[no-untyped-def]
    """Tạo thêm client độc lập (mỗi client một bộ cookie) cho kiểm thử nhiều người dùng."""
    clients: list[TestClient] = []

    def factory() -> TestClient:
        c = TestClient(app, headers={"Origin": ORIGIN})
        c.__enter__()
        clients.append(c)
        return c

    yield factory
    for c in clients:
        c.__exit__(None, None, None)
