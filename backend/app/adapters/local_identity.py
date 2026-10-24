"""Adapter tài khoản nội bộ (DQ-003 = không có IdP): Argon2id, giới hạn đăng nhập sai.

- Giới hạn `LOGIN_MAX_FAILURES` lần sai trong `LOGIN_FAILURE_WINDOW_MINUTES`, đếm riêng theo tài khoản
  và theo địa chỉ; vượt giới hạn thì khóa tạm cho tới khi các lần sai cũ ra khỏi cửa sổ.
- Không phân biệt "không có tài khoản" với "sai mật khẩu": cả hai cùng kết quả, và khi không có tài
  khoản vẫn chạy một lần kiểm tra băm giả để thời gian phản hồi tương đương.
"""

from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.access.models import LoginFailure, User
from app.ports.identity import AuthenticatedUser, AuthFailure, AuthResult

ADDRESS_LIMIT_FACTOR = 4


class LocalIdentityProvider:
    def __init__(
        self, sessions: sessionmaker[Session], max_failures: int, window_minutes: int
    ) -> None:
        self._sessions = sessions
        self._max_failures = max_failures
        self._window = timedelta(minutes=window_minutes)
        self._hasher = PasswordHasher()  # mặc định của argon2-cffi là Argon2id
        self._dummy_hash = self._hasher.hash("mat-khau-gia-de-can-bang-thoi-gian")

    def hash_password(self, password: str) -> str:
        return self._hasher.hash(password)

    def set_password(self, login: str, password: str) -> None:
        with self._sessions() as session, session.begin():
            user = session.scalar(select(User).where(User.login == login))
            if user is None:
                raise LookupError(login)
            user.password_hash = self.hash_password(password)

    def authenticate(self, login: str, password: str, client_addr: str) -> AuthResult:
        login = login.strip()
        now = datetime.now(UTC)
        with self._sessions() as session, session.begin():
            if self._is_locked(session, login, client_addr, now):
                return AuthResult(None, AuthFailure.LOCKED)

            user = session.scalar(select(User).where(User.login == login))
            stored = user.password_hash if user is not None else None
            if not self._verify(stored, password) or user is None:
                session.add(LoginFailure(login=login, client_addr=client_addr, at=now))
                return AuthResult(None, AuthFailure.INVALID_CREDENTIALS)

            # Đăng nhập đúng: xóa các lần sai của tài khoản này
            session.execute(delete(LoginFailure).where(LoginFailure.login == login))
            if stored is not None and self._hasher.check_needs_rehash(stored):
                user.password_hash = self.hash_password(password)
            return AuthResult(AuthenticatedUser(user.id, user.login, user.display_name))

    def _verify(self, stored: str | None, password: str) -> bool:
        # Luôn chạy đúng một phép kiểm tra Argon2 để thời gian không tiết lộ tài khoản có tồn tại không
        try:
            return self._hasher.verify(stored or self._dummy_hash, password) and stored is not None
        except (VerificationError, InvalidHashError):
            return False

    def _is_locked(self, session: Session, login: str, client_addr: str, now: datetime) -> bool:
        since = now - self._window
        by_login = session.scalar(
            select(func.count())
            .select_from(LoginFailure)
            .where(LoginFailure.login == login, LoginFailure.at >= since)
        )
        by_addr = session.scalar(
            select(func.count())
            .select_from(LoginFailure)
            .where(LoginFailure.client_addr == client_addr, LoginFailure.at >= since)
        )
        # Dọn bản ghi cũ để bảng không phình
        session.execute(
            delete(LoginFailure).where(
                LoginFailure.at < since,
                or_(LoginFailure.login == login, LoginFailure.client_addr == client_addr),
            )
        )
        # Theo địa chỉ dùng ngưỡng rộng hơn: nhiều người trong văn phòng có thể chung một địa chỉ NAT,
        # nhưng vẫn chặn được việc thử một mật khẩu trên nhiều tài khoản.
        return (by_login or 0) >= self._max_failures or (
            by_addr or 0
        ) >= self._max_failures * ADDRESS_LIMIT_FACTOR
