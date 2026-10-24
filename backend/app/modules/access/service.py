"""Phiên đăng nhập và quyền truy cập (M-03, US-017).

Vai trò luôn lấy từ `access_grants` (không lấy từ IdP). Người đăng nhập đúng nhưng không có quyền
`active` không được dùng hệ thống (403 `no_access`), và người bị thu hồi mất truy cập ở yêu cầu kế tiếp
vì mọi yêu cầu đều đọc lại trạng thái quyền.
"""

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.errors import AppError, bad_request, not_found
from app.modules.access.models import AccessGrant, User, UserSession

ROLE_BD = "bd"
ROLE_MANAGER = "manager"
ROLE_SECURITY_ADMIN = "security_admin"


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    login: str
    display_name: str | None
    role: str


class SessionExpired(Exception):
    pass


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def create_session(db: Session, user_id: uuid.UUID) -> str:
    """Tạo phiên mới, trả mã ngẫu nhiên để đặt vào cookie (bảng chỉ lưu bản băm)."""
    token = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    db.add(
        UserSession(
            token_hash=_hash_token(token), user_id=user_id, created_at=now, last_seen_at=now
        )
    )
    return token


def end_session(db: Session, token: str) -> None:
    db.execute(delete(UserSession).where(UserSession.token_hash == _hash_token(token)))


def resolve_session(db: Session, token: str, idle_hours: float) -> User:
    """Trả người dùng của phiên và gia hạn phiên. Hết hạn hoặc không tồn tại → SessionExpired."""
    row = db.get(UserSession, _hash_token(token))
    now = datetime.now(UTC)
    if row is None:
        raise SessionExpired
    if now - row.last_seen_at > timedelta(hours=idle_hours):
        db.delete(row)
        raise SessionExpired
    user = db.get(User, row.user_id)
    if user is None:
        raise SessionExpired
    row.last_seen_at = now
    return user


def active_role(db: Session, user_id: uuid.UUID) -> str | None:
    grant = db.get(AccessGrant, user_id)
    if grant is None or grant.status != "active":
        return None
    return grant.role


def find_or_create_user(db: Session, login: str, display_name: str | None = None) -> User:
    login = login.strip()
    user = db.scalar(select(User).where(User.login == login))
    if user is None:
        user = User(id=uuid.uuid4(), login=login, display_name=display_name)
        db.add(user)
        db.flush()
    elif display_name and not user.display_name:
        user.display_name = display_name
    return user


@dataclass(frozen=True)
class GrantView:
    user_id: uuid.UUID
    login: str
    display_name: str | None
    role: str
    status: str
    granted_at: datetime
    revoked_at: datetime | None


def list_grants(db: Session) -> list[GrantView]:
    rows = db.execute(
        select(AccessGrant, User).join(User, User.id == AccessGrant.user_id).order_by(User.login)
    ).all()
    return [
        GrantView(u.id, u.login, u.display_name, g.role, g.status, g.granted_at, g.revoked_at)
        for g, u in rows
    ]


def grant_access(db: Session, login: str, role: str, granted_by: uuid.UUID) -> GrantView:
    if role not in (ROLE_BD, ROLE_MANAGER, ROLE_SECURITY_ADMIN):
        raise bad_request("invalid_role", "Vai trò không hợp lệ.")
    if not login.strip():
        raise bad_request("invalid_login", "Tên đăng nhập không được để trống.")
    user = find_or_create_user(db, login)
    now = datetime.now(UTC)
    grant = db.get(AccessGrant, user.id)
    if grant is None:
        grant = AccessGrant(user_id=user.id, role=role, status="active", granted_by=granted_by)
        grant.granted_at = now
        db.add(grant)
    else:
        grant.role = role
        grant.status = "active"
        grant.granted_by = granted_by
        grant.granted_at = now
        grant.revoked_at = None
    db.flush()
    return GrantView(
        user.id, user.login, user.display_name, grant.role, grant.status, now, grant.revoked_at
    )


def revoke_access(db: Session, user_id: uuid.UUID, by: uuid.UUID) -> None:
    """Đặt `revoked`, không xóa bản ghi. Xóa luôn các phiên đang mở của người đó."""
    grant = db.get(AccessGrant, user_id)
    if grant is None:
        raise not_found("grant_not_found", "Không tìm thấy người dùng.")
    if user_id == by:
        raise AppError(409, "cannot_revoke_self", "Không thể tự thu hồi quyền của chính mình.")
    grant.status = "revoked"
    grant.revoked_at = datetime.now(UTC)
    db.execute(delete(UserSession).where(UserSession.user_id == user_id))
