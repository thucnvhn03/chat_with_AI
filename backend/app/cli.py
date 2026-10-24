"""Lệnh quản trị.

    python -m app.cli create-admin <login>     # tạo tài khoản quản trị bảo mật đầu tiên
    python -m app.cli create-user <login> <role>  # tiện cho môi trường phát triển/kiểm thử
    python -m app.cli set-password <login>

Mật khẩu đọc từ biến môi trường INITIAL_PASSWORD nếu có, nếu không thì hỏi trên terminal (không hiện).
Không có màn hình tự đăng ký (US-017).
"""

import argparse
import getpass
import os
import sys

from app.config import get_settings
from app.container import build_identity
from app.db import make_engine, make_session_factory, transaction
from app.modules.access.models import AccessGrant
from app.modules.access.service import ROLE_SECURITY_ADMIN, find_or_create_user


def _read_password() -> str:
    password = os.environ.get("INITIAL_PASSWORD")
    if password:
        return password
    first = getpass.getpass("Mật khẩu: ")
    if first != getpass.getpass("Nhập lại mật khẩu: "):
        sys.exit("Hai lần nhập không khớp.")
    return first


MIN_PASSWORD_CHARS = 12


def _download_model() -> None:
    settings = get_settings()
    if settings.embedding_provider != "local":
        print("EMBEDDING_PROVIDER khác local: không cần tải mô hình.")
        return
    from huggingface_hub import snapshot_download

    # Bỏ bản ONNX và ảnh minh họa của kho mô hình (vài GB) — sentence-transformers chỉ cần trọng số PyTorch
    path = snapshot_download(
        settings.embedding_model,
        ignore_patterns=["onnx/*", "*.onnx", "*.onnx_data", "imgs/*", "*.h5"],
    )
    print(f"Mô hình {settings.embedding_model} sẵn sàng ở {path}")


def _create(login: str, role: str, with_password: bool) -> None:
    settings = get_settings()
    sessions = make_session_factory(make_engine(settings.database_url))
    with transaction(sessions) as db:
        user = find_or_create_user(db, login)
        grant = db.get(AccessGrant, user.id)
        if grant is None:
            db.add(AccessGrant(user_id=user.id, role=role, status="active"))
        else:
            grant.role, grant.status, grant.revoked_at = role, "active", None
    if with_password:
        password = _read_password()
        if len(password) < MIN_PASSWORD_CHARS:
            sys.exit(f"Mật khẩu cần ít nhất {MIN_PASSWORD_CHARS} ký tự.")
        build_identity(settings, sessions).set_password(login, password)
    print(f"Đã cấp vai trò {role} cho {login}.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    admin = sub.add_parser("create-admin", help="Tạo tài khoản quản trị bảo mật")
    admin.add_argument("login")
    user = sub.add_parser("create-user", help="Tạo tài khoản với vai trò cho trước")
    user.add_argument("login")
    user.add_argument("role", choices=["bd", "manager", "security_admin"])
    pw = sub.add_parser("set-password", help="Đặt lại mật khẩu tài khoản nội bộ")
    pw.add_argument("login")
    sub.add_parser(
        "download-model",
        help="Tải mô hình embedding vào HF_HOME một lần (trước khi chạy backend/worker)",
    )
    args = parser.parse_args(argv)

    if args.command == "download-model":
        _download_model()
        return
    with_password = get_settings().auth_mode == "local"
    if args.command == "create-admin":
        _create(args.login, ROLE_SECURITY_ADMIN, with_password)
    elif args.command == "create-user":
        _create(args.login, args.role, with_password)
    else:
        settings = get_settings()
        sessions = make_session_factory(make_engine(settings.database_url))
        build_identity(settings, sessions).set_password(args.login, _read_password())
        print("Đã đặt mật khẩu.")


if __name__ == "__main__":
    main()
