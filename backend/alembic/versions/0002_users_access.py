"""Người dùng, quyền truy cập, phiên, lần đăng nhập sai (T1-01, T1-02, T1-04).

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("login", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text()),
        sa.Column("password_hash", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_users_login", "users", ["login"], unique=True)

    op.create_table(
        "access_grants",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("granted_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column(
            "granted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "role IN ('bd', 'manager', 'security_admin')", name="ck_access_grants_role"
        ),
        sa.CheckConstraint("status IN ('active', 'revoked')", name="ck_access_grants_status"),
    )

    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])

    op.create_table(
        "login_failures",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("login", sa.Text(), nullable=False),
        sa.Column("client_addr", sa.Text(), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_login_failures_login", "login_failures", ["login"])
    op.create_index("ix_login_failures_client_addr", "login_failures", ["client_addr"])


def downgrade() -> None:
    op.drop_table("login_failures")
    op.drop_table("sessions")
    op.drop_table("access_grants")
    op.drop_index("ix_users_login", table_name="users")
    op.drop_table("users")
