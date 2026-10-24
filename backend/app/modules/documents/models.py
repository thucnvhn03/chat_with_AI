"""Bảng tài liệu (M-04). BR-001..005, BR-018, BR-024."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

DOCUMENT_STATUSES = ("uploading", "processing", "ready", "failed", "deleting", "deleted")
FAILURE_REASONS = (
    "corrupted",
    "encrypted",
    "not_pdf",
    "too_large",
    "no_text",
    "network",
    "internal",
)


def _in(values: tuple[str, ...]) -> str:
    return "(" + ", ".join(f"'{v}'" for v in values) + ")"


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(f"status IN {_in(DOCUMENT_STATUSES)}", name="ck_documents_status"),
        CheckConstraint(
            f"failure_reason IS NULL OR failure_reason IN {_in(FAILURE_REASONS)}",
            name="ck_documents_failure_reason",
        ),
        Index("ix_documents_owner_status", "owner_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_name: Mapped[str] = mapped_column(Text)
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    page_count: Mapped[int | None] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Thời điểm xóa vĩnh viễn hoàn tất (AC-024)
    purged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
