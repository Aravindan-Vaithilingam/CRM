from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def record_audit(db: Session, entity_type: str, entity_id: str, action: str, actor_id: str, data: dict | None = None):
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_id=actor_id,
        data=data,
        created_at=datetime.utcnow(),
    )
    db.add(log)
