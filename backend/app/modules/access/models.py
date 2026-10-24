"""Bảng của mô-đun truy cập (M-03): người dùng, quyền, phiên, đăng nhập sai, ACL tài liệu."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

ROLES = ("bd", "manager", "security_admin")
GRANT_STATUSES = ("active", "revoked")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login: Mapped[str] = mapped_column(Text, unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(Text)
    # Chỉ dùng khi không có IdP (DQ-003). Băm Argon2id.
    password_hash: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AccessGrant(Base):
    """UC-15, BR-014. Một vai trò mỗi người (DQ-002); thu hồi = đổi trạng thái, không xóa bản ghi."""

    __tablename__ = "access_grants"
    __table_args__ = (
        CheckConstraint(
            "role IN ('bd', 'manager', 'security_admin')", name="ck_access_grants_role"
        ),
        CheckConstraint("status IN ('active', 'revoked')", name="ck_access_grants_status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    granted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserSession(Base):
    """Phiên lưu phía máy chủ. Cookie chỉ chứa mã ngẫu nhiên; bảng lưu bản băm SHA-256 của mã."""

    __tablename__ = "sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class LoginFailure(Base):
    """Lần đăng nhập sai, để giới hạn theo tài khoản và theo địa chỉ (implement_plan.md mục 6.1)."""

    __tablename__ = "login_failures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(Text, index=True)
    client_addr: Mapped[str] = mapped_column(Text, index=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DocumentAcl(Base):
    """BR-020. Chia sẻ tài liệu cho người khác; để trống cho tới khi OQ-003 cho phép chia sẻ."""

    __tablename__ = "document_acl"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
