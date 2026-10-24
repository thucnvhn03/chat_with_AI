"""IF-06: trang nguồn và tệp gốc (US-014, US-015), sự kiện mở nguồn (T2-11).

Tệp gốc luôn đi qua backend (không trả đường dẫn kho) để luôn được kiểm quyền.
"""

import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_runtime
from app.api.security import require_role
from app.modules.access.service import ROLE_BD, CurrentUser
from app.modules.sources import service
from app.modules.usage import events

router = APIRouter(tags=["sources"])

bd_only = require_role(ROLE_BD)


class PageOut(BaseModel):
    page: int
    page_count: int
    text: str
    document_name: str


class SourceOpenedIn(BaseModel):
    document_id: uuid.UUID
    page: int = Field(ge=1)


@router.get("/documents/{document_id}/pages/{page}", response_model=PageOut)
def get_page(
    document_id: uuid.UUID,
    page: int,
    request: Request,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> PageOut:
    view = service.page_text(db, get_runtime(request).file_store, user.id, document_id, page)
    return PageOut(**view.__dict__)


@router.get(
    "/documents/{document_id}/file",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
)
def get_file(
    document_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> Response:
    name, data = service.original_file(db, get_runtime(request).file_store, user.id, document_id)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{quote(name)}",
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post("/events/source-opened", status_code=204)
def source_opened(
    body: SourceOpenedIn,
    db: Session = Depends(get_db, scope="function"),
    user: CurrentUser = Depends(bd_only),
) -> Response:
    """Chỉ nhận id tài liệu và số trang; không nhận nội dung. Kiểm quyền với tài liệu."""
    service.ensure_readable(db, user.id, body.document_id)
    events.record(db, user.id, events.SOURCE_OPENED, page=body.page)
    return Response(status_code=204)
