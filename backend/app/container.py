"""Gốc lắp ghép: chọn adapter cụ thể theo cấu hình. Chỉ `main.py`, worker và CLI import tệp này."""

from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.fake_llm import FakeAnswerGenerator
from app.adapters.hash_embedding import HashEmbeddingProvider
from app.adapters.local_identity import LocalIdentityProvider
from app.adapters.s3_file_store import S3FileStore
from app.config import Settings
from app.db import make_engine, make_session_factory
from app.modules.jobs.models import Job
from app.observability.health import CheckResult, HealthCheck
from app.observability.logging import get_logger
from app.ports.ai import AnswerGenerator, EmbeddingProvider
from app.ports.identity import OidcClient
from app.ports.storage import FileStore
from app.runtime import Runtime

log = get_logger("container")


def build_identity(settings: Settings, sessions: sessionmaker[Session]) -> LocalIdentityProvider:
    return LocalIdentityProvider(
        sessions, settings.login_max_failures, settings.login_failure_window_minutes
    )


def build_file_store(settings: Settings) -> S3FileStore:
    store = S3FileStore(
        bucket=settings.s3_bucket,
        endpoint_url=settings.s3_endpoint_url,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        region=settings.s3_region,
        server_side_encryption=settings.s3_server_side_encryption,
    )
    if settings.s3_create_bucket:
        store.ensure_bucket()
    return store


def build_embedder(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "hash":
        return HashEmbeddingProvider(settings.embedding_dim)
    from app.adapters.local_embedding import LocalEmbeddingProvider

    log.info("embedding_model_loading", model=settings.embedding_model)
    return LocalEmbeddingProvider(
        settings.embedding_model, settings.embedding_dim, settings.embed_batch
    )


def build_answer_generator(settings: Settings) -> AnswerGenerator:
    if settings.answer_provider == "fake":
        return FakeAnswerGenerator()
    from app.adapters.claude_llm import ClaudeAnswerGenerator

    return ClaudeAnswerGenerator(
        model=settings.answer_model,
        effort=settings.answer_effort,
        max_tokens=settings.answer_max_tokens,
        max_retries=settings.answer_max_retries,
        server_fallback=settings.answer_server_fallback,
        api_key=settings.anthropic_api_key,
    )


def build_oidc(settings: Settings) -> OidcClient | None:
    if settings.auth_mode != "oidc":
        return None
    from app.adapters.oidc_identity import OidcIdentityClient

    if not (settings.oidc_issuer and settings.oidc_client_id and settings.oidc_redirect_uri):
        raise ValueError("AUTH_MODE=oidc cần OIDC_ISSUER, OIDC_CLIENT_ID, OIDC_REDIRECT_URI")
    return OidcIdentityClient(
        settings.oidc_issuer,
        settings.oidc_client_id,
        settings.oidc_client_secret,
        settings.oidc_redirect_uri,
        settings.oidc_scopes,
    )


def default_health_checks(
    settings: Settings, sessions: sessionmaker[Session], file_store: FileStore
) -> dict[str, HealthCheck]:
    """Kiểm tra cơ sở dữ liệu, kho tệp, hàng đợi (US-021, T4-04)."""

    def database() -> CheckResult:
        with sessions() as db:
            db.execute(text("SELECT 1"))
        return CheckResult(True)

    def storage() -> CheckResult:
        file_store.check()
        return CheckResult(True)

    def queue() -> CheckResult:
        with sessions() as db:
            oldest = db.scalar(select(func.min(Job.run_after)).where(Job.status == "queued"))
        if oldest is None:
            return CheckResult(True)
        age = (datetime.now(UTC) - oldest).total_seconds()
        if age > settings.queue_max_age_s:
            return CheckResult(False, "queue_backlog")
        return CheckResult(True)

    return {"database": database, "storage": storage, "queue": queue}


def build_runtime(settings: Settings, role: Literal["api", "worker"]) -> Runtime:
    engine = make_engine(settings.database_url)
    sessions = make_session_factory(engine)
    file_store = build_file_store(settings)
    return Runtime(
        settings=settings,
        engine=engine,
        sessions=sessions,
        file_store=file_store,
        embedder=build_embedder(settings),
        # Worker không sinh câu trả lời, nhưng giữ cùng kiểu Runtime cho đơn giản
        answer_generator=build_answer_generator(settings)
        if role == "api"
        else FakeAnswerGenerator(),
        identity=build_identity(settings, sessions),
        oidc=build_oidc(settings) if role == "api" else None,
        health_checks=default_health_checks(settings, sessions, file_store),
    )
