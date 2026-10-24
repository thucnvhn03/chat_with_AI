"""Gom các router của lớp API (M-02)."""

from fastapi import APIRouter, Depends

from app.api import (
    admin_access,
    admin_audit,
    auth,
    conversations,
    documents,
    health,
    reports,
    sources,
)
from app.api.security import check_origin

health_router = health.router

# Mọi yêu cầu thay đổi dữ liệu dưới /api/v1 phải qua kiểm tra nguồn gốc (CSRF)
api_router = APIRouter(dependencies=[Depends(check_origin)])
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(sources.router)
api_router.include_router(conversations.router)
api_router.include_router(admin_access.router)
api_router.include_router(admin_audit.router)
api_router.include_router(reports.router)
