from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import (
    get_current_user,
    ROLE_APPROVER,
    CurrentUser,
)
from app.models.project import Project, ProjectVersion
from app.models.approval import ApprovalEvent
from app.models.common import ProjectStatus, ApprovalAction
from app.schemas.approval import ApprovalActionIn, ApprovalEventOut
from app.schemas.project import ProjectVersionOut
from app.services.audit import record_audit

router = APIRouter()


@router.get("/pending", response_model=list[ProjectVersionOut])
def list_pending(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_APPROVER:
        raise HTTPException(
            status_code=403,
            detail="Only approvers can view pending approvals",
        )

    return (
        db.query(ProjectVersion)
        .filter(ProjectVersion.status == ProjectStatus.pending.value)
        .all()
    )


@router.post("/{version_id}/approve", response_model=ApprovalEventOut)
def approve_project(
    version_id: int,
    payload: ApprovalActionIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_APPROVER:
        raise HTTPException(403, "Only approvers can approve")

    version = db.get(ProjectVersion, version_id)
    if version is None or version.status != ProjectStatus.pending.value:
        raise HTTPException(400, "Project version not pending")

    # Make it approved and active
    version.status = ProjectStatus.approved.value
    version.approved_at = datetime.utcnow()
    version.is_active = True

    project = db.get(Project, version.project_id)

    # deactivate previous active version
    if project.active_version_id and project.active_version_id != version.id:
        previous = db.get(ProjectVersion, project.active_version_id)
        if previous:
            previous.is_active = False

    project.active_version_id = version.id

    event = ApprovalEvent(
        project_version_id=version.id,
        action=ApprovalAction.approved.value,
        actor_id=user.user_id,
        comment=payload.comment,
        created_at=datetime.utcnow(),
    )
    db.add(event)

    record_audit(
        db,
        entity="project_version",
        entity_id=str(version.id),
        action="approve",
        user_id=user.user_id,
        meta={"comment": payload.comment},
    )

    db.commit()
    db.refresh(event)
    return event


@router.post("/{version_id}/reject", response_model=ApprovalEventOut)
def reject_project(
    version_id: int,
    payload: ApprovalActionIn,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_APPROVER:
        raise HTTPException(403, "Only approvers can reject")

    version = db.get(ProjectVersion, version_id)
    if version is None or version.status != ProjectStatus.pending.value:
        raise HTTPException(400, "Project version not pending")

    version.status = ProjectStatus.rejected.value
    version.rejected_at = datetime.utcnow()
    version.rejection_comment = payload.comment

    event = ApprovalEvent(
        project_version_id=version.id,
        action=ApprovalAction.rejected.value,
        actor_id=user.user_id,
        comment=payload.comment,
        created_at=datetime.utcnow(),
    )
    db.add(event)

    record_audit(
        db,
        entity="project_version",
        entity_id=str(version.id),
        action="reject",
        user_id=user.user_id,
        meta={"comment": payload.comment},
    )

    db.commit()
    db.refresh(event)
    return event
