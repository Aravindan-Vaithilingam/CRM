from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogOut

router = APIRouter()


@router.get("", response_model=list[AuditLogOut])
def list_audit(
    entity_type: str | None = None,
    entity_id: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)

    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    return (
        query
        .order_by(AuditLog.created_at.desc())
        .all()
    )
