"""Bảng chia sẻ tài liệu `document_acl` (T3-03, BR-020).

Phạm vi chia sẻ chờ OQ-003. Cho tới khi có quyết định, bảng để trống và không có endpoint ghi vào nó:
mỗi người chỉ thấy tài liệu do chính mình tải lên.

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_acl",
        sa.Column(
            "document_id",
            UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
    )
    op.create_index("ix_document_acl_user_id", "document_acl", ["user_id"])


def downgrade() -> None:
    op.drop_table("document_acl")
