from datetime import datetime
from pydantic import BaseModel

class AuditLogOut(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    action: str
    actor_id: int
    created_at: datetime
    data: dict | None

    class Config:
        from_attributes = True
