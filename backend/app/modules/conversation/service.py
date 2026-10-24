"""Hội thoại và ngữ cảnh hội thoại (M-08, US-010).

Hội thoại chỉ do chủ hội thoại truy cập; người khác nhận 404. Lưu hội thoại giữa các phiên chờ PQ-004:
giao diện mặc định chỉ giữ hội thoại trong phiên (tạo hội thoại mới khi mở ứng dụng).
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.errors import not_found
from app.modules.conversation.models import Citation, Conversation, Message
from app.modules.qa.service import QAResult
from app.modules.usage.models import Feedback


def create_conversation(db: Session, user_id: uuid.UUID) -> Conversation:
    conversation = Conversation(id=uuid.uuid4(), user_id=user_id)
    db.add(conversation)
    db.flush()
    return conversation


def get_owned(db: Session, user_id: uuid.UUID, conversation_id: uuid.UUID) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != user_id:
        raise not_found("conversation_not_found", "Không tìm thấy hội thoại.")
    return conversation


def history_for_model(db: Session, conversation_id: uuid.UUID, turns: int) -> list[dict[str, str]]:
    """`turns` lượt hỏi-đáp gần nhất, dạng tin nhắn cho mô hình (cũ trước, mới sau)."""
    if turns <= 0:
        return []
    rows = list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Message.role.desc())
            .limit(turns * 2)
        )
    )
    rows.reverse()
    # Bắt đầu bằng câu hỏi của người dùng (API yêu cầu tin nhắn đầu là `user`)
    while rows and rows[0].role != "user":
        rows.pop(0)
    return [{"role": m.role, "content": m.content} for m in rows]


def save_turn(
    db: Session,
    conversation_id: uuid.UUID,
    question: str,
    result: QAResult,
    latency_ms: int,
    asked_at: datetime,
) -> Message:
    db.add(
        Message(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            role="user",
            content=question,
            created_at=asked_at,
        )
    )
    answer = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        role="assistant",
        content=result.answer,
        not_found=result.not_found,
        latency_ms=latency_ms,
        # Bảo đảm câu trả lời luôn xếp sau câu hỏi
        created_at=max(datetime.now(UTC), asked_at + timedelta(microseconds=1)),
    )
    db.add(answer)
    db.flush()
    for ordinal, c in enumerate(result.citations):
        db.add(
            Citation(
                message_id=answer.id,
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                document_name=c.document_name,
                page=c.page,
                cited_text=c.cited_text,
                ordinal=ordinal,
            )
        )
    return answer


@dataclass(frozen=True)
class CitationView:
    document_id: uuid.UUID
    document_name: str
    page: int
    cited_text: str | None


@dataclass(frozen=True)
class MessageView:
    id: uuid.UUID
    role: str
    content: str
    not_found: bool
    latency_ms: int | None
    created_at: datetime
    citations: list[CitationView]
    feedback: str | None


def list_messages(db: Session, conversation_id: uuid.UUID) -> list[MessageView]:
    messages = list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.role.desc())
        )
    )
    ids = [m.id for m in messages]
    citations: dict[uuid.UUID, list[CitationView]] = {}
    for c in db.scalars(
        select(Citation).where(Citation.message_id.in_(ids)).order_by(Citation.ordinal)
    ):
        citations.setdefault(c.message_id, []).append(
            CitationView(c.document_id, c.document_name, c.page, c.cited_text)
        )
    feedback = {
        f.message_id: f.value
        for f in db.scalars(select(Feedback).where(Feedback.message_id.in_(ids)))
    }
    return [
        MessageView(
            m.id,
            m.role,
            m.content,
            m.not_found,
            m.latency_ms,
            m.created_at,
            citations.get(m.id, []),
            feedback.get(m.id),
        )
        for m in messages
    ]


def owned_assistant_message(db: Session, user_id: uuid.UUID, message_id: uuid.UUID) -> Message:
    row = db.execute(
        select(Message, Conversation)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .where(Message.id == message_id)
    ).first()
    if row is None or row[1].user_id != user_id or row[0].role != "assistant":
        raise not_found("message_not_found", "Không tìm thấy câu trả lời.")
    return row[0]


def cleanup_inactive(db: Session, retention_days: int) -> int:
    """Xóa hội thoại không có hoạt động trong `retention_days` ngày (PQ-004).

    Xóa hội thoại kéo theo tin nhắn, trích dẫn và đánh giá (ON DELETE CASCADE). Trả số hội thoại đã xóa.
    """
    if retention_days <= 0:
        return 0
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    last_activity = (
        select(func.max(Message.created_at))
        .where(Message.conversation_id == Conversation.id)
        .correlate(Conversation)
        .scalar_subquery()
    )
    stale = select(Conversation.id).where(
        Conversation.created_at < cutoff,
        or_(last_activity.is_(None), last_activity < cutoff),
    )
    result = db.execute(delete(Conversation).where(Conversation.id.in_(stale)))
    return int(getattr(result, "rowcount", 0) or 0)
