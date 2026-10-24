"""IF-05: hội thoại và hỏi đáp (US-008..015); IF-07: đánh giá câu trả lời (US-024).

Thân yêu cầu (câu hỏi) không bao giờ được ghi log. Bản ghi kiểm toán và sự kiện `question_submitted`
được ghi và commit TRƯỚC khi gọi dịch vụ AI, không chứa nội dung câu hỏi.
"""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_runtime
from app.api.security import require_role
from app.errors import AppError, bad_request
from app.modules.access.scope import allowed_document_ids
from app.modules.access.service import ROLE_BD, CurrentUser
from app.modules.audit import service as audit
from app.modules.conversation import service as conversations
from app.modules.qa.service import QAResult, answer_question
from app.modules.retrieval.search import RetrievedChunk, search
from app.modules.usage import events
from app.modules.usage.reports import set_feedback
from app.observability.logging import get_logger
from app.observability.metrics import ANSWER_LATENCY, ANSWERS
from app.ports.ai import AnswerGenerationError, AnswerTimeoutError
from app.runtime import Runtime

router = APIRouter(tags=["conversations"])
log = get_logger("api.conversations")

bd_only = require_role(ROLE_BD)

# Luồng chạy phần hỏi đáp để áp hạn ANSWER_TIMEOUT_S cho toàn bộ chuỗi nhúng → truy xuất → sinh
_executor = ThreadPoolExecutor(max_workers=16, thread_name_prefix="qa")


class ConversationOut(BaseModel):
    id: uuid.UUID


class QuestionIn(BaseModel):
    question: str


class CitationOut(BaseModel):
    document_id: uuid.UUID
    document_name: str
    page: int
    cited_text: str | None


class AnswerOut(BaseModel):
    message_id: uuid.UUID
    answer: str
    not_found: bool
    citations: list[CitationOut]
    latency_ms: int


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    not_found: bool
    latency_ms: int | None
    created_at: datetime
    citations: list[CitationOut]
    feedback: str | None


class FeedbackIn(BaseModel):
    value: Literal["helpful", "not_helpful"]


@router.post("/conversations", response_model=ConversationOut, status_code=201)
def create_conversation(
    db: Session = Depends(get_db, scope="function"), user: CurrentUser = Depends(bd_only)
) -> ConversationOut:
    return ConversationOut(id=conversations.create_conversation(db, user.id).id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> list[MessageOut]:
    conversations.get_owned(db, user.id, conversation_id)
    return [
        MessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            not_found=m.not_found,
            latency_ms=m.latency_ms,
            created_at=m.created_at,
            citations=[CitationOut(**c.__dict__) for c in m.citations],
            feedback=m.feedback,
        )
        for m in conversations.list_messages(db, conversation_id)
    ]


def _validate_question(raw: str, max_chars: int) -> str:
    question = raw.strip()
    if not question:
        raise bad_request("question_empty", "Hãy nhập câu hỏi.")
    if len(question) > max_chars:
        raise bad_request(
            "question_too_long", f"Câu hỏi dài quá {max_chars} ký tự. Hãy rút gọn câu hỏi."
        )
    return question


def _run_qa(
    runtime: Runtime,
    question: str,
    history: list[dict[str, str]],
    allowed: set[uuid.UUID],
) -> QAResult:
    settings = runtime.settings

    def retrieve(vector: list[float]) -> list[RetrievedChunk]:
        # Phiên riêng cho luồng này (phiên của yêu cầu không dùng chung giữa các luồng)
        with runtime.sessions() as db, db.begin():
            return search(
                db,
                vector,
                allowed,
                settings.top_k,
                settings.max_chunks_per_doc,
                settings.hnsw_ef_search,
            )

    return answer_question(
        question,
        history,
        runtime.embedder,
        retrieve,
        runtime.answer_generator,
        settings.min_relevance_score,
        settings.answer_timeout_s,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=AnswerOut)
def ask(
    conversation_id: uuid.UUID,
    body: QuestionIn,
    request: Request,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> AnswerOut:
    runtime = get_runtime(request)
    settings = runtime.settings
    started = time.perf_counter()
    asked_at = datetime.now(UTC)
    question = _validate_question(body.question, settings.max_question_chars)
    conversations.get_owned(db, user.id, conversation_id)
    allowed = allowed_document_ids(db, user.id)
    history = conversations.history_for_model(db, conversation_id, settings.history_turns)

    # Bước 2 của mục 5.3: kiểm toán + sự kiện, commit riêng trước khi gọi dịch vụ AI
    with runtime.sessions() as audit_db, audit_db.begin():
        audit.record(audit_db, user.id, list(allowed))
        events.record(audit_db, user.id, events.QUESTION_SUBMITTED)

    future = _executor.submit(_run_qa, runtime, question, history, allowed)
    try:
        result = future.result(timeout=settings.answer_timeout_s)
    except (FutureTimeout, AnswerTimeoutError):
        ANSWERS.labels("timeout").inc()
        log.warning("answer_timeout", timeout_s=settings.answer_timeout_s)
        raise AppError(
            504, "answer_timeout", "Hệ thống trả lời quá lâu. Câu hỏi vẫn được giữ, hãy thử lại."
        ) from None
    except AnswerGenerationError:
        ANSWERS.labels("error").inc()
        raise AppError(
            502, "answer_unavailable", "Chưa trả lời được lúc này. Hãy thử lại sau ít phút."
        ) from None
    if result.refused:
        ANSWERS.labels("refused").inc()
        raise AppError(
            502, "answer_unavailable", "Chưa trả lời được câu hỏi này. Hãy thử diễn đạt khác."
        )

    latency_ms = int((time.perf_counter() - started) * 1000)
    message = conversations.save_turn(db, conversation_id, question, result, latency_ms, asked_at)
    ANSWER_LATENCY.observe(latency_ms / 1000)
    ANSWERS.labels("not_found" if result.not_found else "answered").inc()
    events.record(
        db,
        user.id,
        events.ANSWER_RETURNED,
        latency_ms=latency_ms,
        sources=len(result.citations),
        not_found=result.not_found,
        not_found_reason=result.reason,
        generator_called=result.generator_called,
        step_ms=result.timings_ms,
    )
    return AnswerOut(
        message_id=message.id,
        answer=result.answer,
        not_found=result.not_found,
        citations=[
            CitationOut(
                document_id=c.document_id,
                document_name=c.document_name,
                page=c.page,
                cited_text=c.cited_text,
            )
            for c in result.citations
        ],
        latency_ms=latency_ms,
    )


@router.put("/messages/{message_id}/feedback", status_code=204)
def put_feedback(
    message_id: uuid.UUID,
    body: FeedbackIn,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> Response:
    conversations.owned_assistant_message(db, user.id, message_id)
    set_feedback(db, message_id, user.id, body.value)
    return Response(status_code=204)
