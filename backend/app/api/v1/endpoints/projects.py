from datetime import datetime, date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import (
    get_current_user,
    ROLE_CREATOR,
    CurrentUser,
)
from app.models.project import Project, ProjectVersion
from app.models.contract import ContractDocument
from app.models.job_category import JobCategory
from app.models.common import ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectOut,
    ProjectVersionOut,
    ProjectUpdate,
)
from app.schemas.job_category import JobCategoryCreate, JobCategoryOut
from app.schemas.contract import ContractOut
from app.services.storage import storage
from app.services.audit import record_audit

router = APIRouter()


def _get_latest_editable_version(db: Session, project_id: int) -> ProjectVersion | None:
    """
    Returns the most recent draft/rejected version that can still be edited.
    """
    editable_states = [
        ProjectStatus.draft.value,
        ProjectStatus.rejected.value,
    ]

    return (
        db.query(ProjectVersion)
        .filter(ProjectVersion.project_id == project_id)
        .filter(ProjectVersion.status.in_(editable_states))
        .order_by(ProjectVersion.version_number.desc())
        .first()
    )


@router.post("", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(403, "Only creators can create projects")

    # Prevent duplicate project codes
    if db.query(Project).filter_by(project_code=payload.project_code).first():
        raise HTTPException(409, "Project code already exists")

    project = Project(
        project_code=payload.project_code,
        client_id=payload.client_id,
        created_by=user.user_id,
        name=payload.project_name,
    )
    db.add(project)
    db.flush()  # ensures project.id is available

    initial_version = ProjectVersion(
        project_id=project.id,
        version_number=1,
        status=ProjectStatus.draft.value,
        project_name=payload.project_name,
        project_start_date=payload.project_start_date,
        project_end_date=payload.project_end_date,
        business_unit=payload.business_unit,
        reviewer_id=payload.reviewer_id,
        creator_id=user.user_id,
        is_active=False,
    )
    db.add(initial_version)

    record_audit(
        db,
        entity="project",
        entity_id=str(project.id),
        action="create",
        user_id=user.user_id,
        meta={"version": 1},
    )

    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    status: str | None = None,
    client_id: int | None = None,
    creator_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Project)

    if client_id is not None:
        query = query.filter(Project.client_id == client_id)

    if creator_id is not None:
        query = query.filter(Project.created_by == creator_id)

    if status:
        query = query.join(ProjectVersion).filter(ProjectVersion.status == status)

    return query.all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.get("/{project_id}/versions", response_model=list[ProjectVersionOut])
def list_versions(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ProjectVersion)
        .filter(ProjectVersion.project_id == project_id)
        .all()
    )


@router.put("/{project_id}/draft", response_model=ProjectVersionOut)
def update_draft(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(403, "Only creators can edit projects")

    version = _get_latest_editable_version(db, project_id)
    if not version:
        raise HTTPException(
            400,
            "No editable draft found. Create a new version first.",
        )

    version.project_name = payload.project_name
    version.project_start_date = payload.project_start_date
    version.project_end_date = payload.project_end_date
    version.business_unit = payload.business_unit
    version.reviewer_id = payload.reviewer_id
    version.creator_id = user.user_id

    record_audit(
        db,
        entity="project_version",
        entity_id=str(version.id),
        action="update",
        user_id=user.user_id,
        meta=payload.model_dump(),
    )

    db.commit()
    db.refresh(version)
    return version


@router.post("/{project_id}/new-version", response_model=ProjectVersionOut)
def create_new_version(
    project_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(403, "Only creators can create new versions")

    project = db.get(Project, project_id)
    if not project or not project.active_version_id:
        raise HTTPException(400, "Project has no active version to copy")

    active_version = db.get(ProjectVersion, project.active_version_id)

    latest_version_number = (
        db.query(ProjectVersion.version_number)
        .filter(ProjectVersion.project_id == project_id)
        .order_by(ProjectVersion.version_number.desc())
        .scalar()
    )

    new_version = ProjectVersion(
        project_id=project_id,
        version_number=latest_version_number + 1,
        status=ProjectStatus.draft.value,
        project_name=active_version.project_name,
        project_start_date=active_version.project_start_date,
        project_end_date=active_version.project_end_date,
        business_unit=active_version.business_unit,
        reviewer_id=active_version.reviewer_id,
        creator_id=user.user_id,
        is_active=False,
    )

    db.add(new_version)

    record_audit(
        db,
        entity="project_version",
        entity_id=str(new_version.id),
        action="create_new_version",
        user_id=user.user_id,
        meta={"copied_from": active_version.id},
    )

    db.commit()
    db.refresh(new_version)
    return new_version


@router.post("/{project_id}/submit", response_model=ProjectVersionOut)
def submit_for_approval(
    project_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(403, "Only creators can submit projects")

    version = _get_latest_editable_version(db, project_id)
    if not version:
        raise HTTPException(400, "No draft available to submit")

    if not db.query(ContractDocument).filter_by(project_version_id=version.id).count():
        raise HTTPException(400, "At least one contract document is required")

    if not db.query(JobCategory).filter_by(project_version_id=version.id).count():
        raise HTTPException(400, "At least one job category is required")

    version.status = ProjectStatus.pending.value
    version.submitted_at = datetime.utcnow()

    record_audit(
        db,
        entity="project_version",
        entity_id=str(version.id),
        action="submit",
        user_id=user.user_id,
        meta=None,
    )

    db.commit()
    db.refresh(version)
    return version


@router.post(
    "/{project_id}/versions/{version_id}/contracts",
    response_model=ContractOut,
)
def upload_contract(
    project_id: int,
    version_id: int,
    document_type: str = Form(...),
    valid_from: str = Form(...),
    valid_till: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(403, "Only creators can upload contracts")

    content = file.file.read()
    storage_key = f"{project_id}/{version_id}/{file.filename}"
    storage.save(storage_key, content)

    contract = ContractDocument(
        project_version_id=version_id,
        document_type=document_type,
        valid_from=date.fromisoformat(valid_from),
        valid_till=date.fromisoformat(valid_till),
        s3_key=storage_key,
        filename=file.filename,
        uploaded_at=datetime.utcnow(),
    )

    db.add(contract)

    record_audit(
        db,
        entity="contract",
        entity_id=str(contract.id),
        action="upload",
        user_id=user.user_id,
        meta={"filename": file.filename},
    )

    db.commit()
    db.refresh(contract)
    return contract


@router.post(
    "/{project_id}/versions/{version_id}/job-categories",
    response_model=list[JobCategoryOut],
)
def add_job_categories(
    project_id: int,
    version_id: int,
    payload: list[JobCategoryCreate],
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(403, "Only creators can add job categories")

    categories: list[JobCategory] = []

    for item in payload:
        category = JobCategory(
            project_version_id=version_id,
            name=item.name,
            rate_card_id=item.rate_card_id,
        )
        db.add(category)
        categories.append(category)

    record_audit(
        db,
        entity="job_category",
        entity_id=str(version_id),
        action="add",
        user_id=user.user_id,
        meta={"count": len(categories)},
    )

    db.commit()
    return categories
