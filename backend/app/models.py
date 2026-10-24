"""Nạp mọi model SQLAlchemy để metadata có đủ bảng (khóa ngoại giữa các mô-đun phân giải được).

Tiến trình nào dùng ORM (API, worker, CLI, Alembic) đều phải import mô-đun này trước khi truy vấn.
"""

from app.modules.access import models as access_models
from app.modules.audit import models as audit_models
from app.modules.conversation import models as conversation_models
from app.modules.documents import models as document_models
from app.modules.ingestion import models as ingestion_models
from app.modules.jobs import models as job_models
from app.modules.usage import models as usage_models

__all__ = [
    "access_models",
    "audit_models",
    "conversation_models",
    "document_models",
    "ingestion_models",
    "job_models",
    "usage_models",
]
