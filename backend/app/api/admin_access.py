"""IF-08: quản lý quyền truy cập (US-017, S-05). Chỉ vai trò `security_admin`."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.security import require_role
from app.modules.access import service
from app.modules.access.service import ROLE_SECURITY_ADMIN, CurrentUser
from app.observability.logging import get_logger

router = APIRouter(prefix="/admin/access", tags=["admin"])
log = get_logger("api.admin_access")

admin_only = require_role(ROLE_SECURITY_ADMIN)


class GrantIn(BaseModel):
    login: str = Field(min_length=1, max_length=200)
    role: str


class GrantOut(BaseModel):
    user_id: uuid.UUID
    login: str
    display_name: str | None
    role: str
    status: str
    granted_at: datetime
    revoked_at: datetime | None


def _out(view: service.GrantView) -> GrantOut:
    return GrantOut(**view.__dict__)


@router.get("", response_model=list[GrantOut])
def list_access(
    db: Session = Depends(get_db, scope="function"), _admin: CurrentUser = Depends(admin_only)
) -> list[GrantOut]:
    return [_out(v) for v in service.list_grants(db)]


@router.post("", response_model=GrantOut, status_code=201)
def grant_access(
    body: GrantIn,
    db: Session = Depends(get_db, scope="function"),
    admin: CurrentUser = Depends(admin_only),
) -> GrantOut:
    view = service.grant_access(db, body.login, body.role, admin.id)
    log.info("access_granted", by=str(admin.id), user_id=str(view.user_id), role=view.role)
    return _out(view)


@router.delete("/{user_id}", status_code=204)
def revoke_access(
    user_id: uuid.UUID,
    db: Session = Depends(get_db, scope="function"),
    admin: CurrentUser = Depends(admin_only),
) -> Response:
    service.revoke_access(db, user_id, admin.id)
    log.info("access_revoked", by=str(admin.id), user_id=str(user_id))
    return Response(status_code=204)
