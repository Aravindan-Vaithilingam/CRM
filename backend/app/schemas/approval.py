from datetime import datetime
from pydantic import BaseModel
from app.models.common import ApprovalAction

class ApprovalActionIn(BaseModel):
    comment: str | None = None

class ApprovalEventOut(BaseModel):
    id: int
    project_version_id: int
    action: ApprovalAction
    actor_id: int
    comment: str | None
    created_at: datetime

    class Config:
        from_attributes = True
