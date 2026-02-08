from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user, ROLE_CREATOR, CurrentUser
from app.models.project import Project, ProjectVersion
from app.models.contract import ContractDocument
from app.models.job_category import JobCategory
from app.models.common import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectOut, ProjectVersionOut, ProjectUpdate
from app.schemas.job_category import JobCategoryCreate, JobCategoryOut
from app.schemas.contract import ContractOut
from app.services.storage import storage
from app.services.audit import record_audit

router = APIRouter()


def _get_latest_draft(db: Session, project_id: str):
    return (
        db.query(ProjectVersion)
        .filter(ProjectVersion.project_id == project_id)
        .filter(ProjectVersion.status.in_([ProjectStatus.draft.value, ProjectStatus.rejected.value]))
        .order_by(ProjectVersion.version_number.desc())
        .first()
    )

@router.post('', response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(status_code=403, detail='Only creators can create projects')
    existing = db.query(Project).filter(Project.project_code == payload.project_code).first()
    if existing:
        raise HTTPException(status_code=409, detail='Project code already exists')

    project = Project(
        project_code=payload.project_code,
        client_id=payload.client_id,
        created_by=user.user_id,
        name=payload.project_name,
    )
    db.add(project)
    db.flush()
    version = ProjectVersion(
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
    db.add(version)
    record_audit(db, 'project', str(project.id), 'create', user.user_id, {'version': 1})
    db.commit()
    db.refresh(project)
    return project

@router.get('', response_model=list[ProjectOut])
def list_projects(
    status: str | None = None,
    client_id: int | None = None,
    creator_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Project)
    if client_id:
        query = query.filter(Project.client_id == client_id)
    if creator_id:
        query = query.filter(Project.created_by == creator_id)
    if status:
        query = query.join(ProjectVersion).filter(ProjectVersion.status == status)
    return query.all()

@router.get('/{project_id}', response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    return project

@router.get('/{project_id}/versions', response_model=list[ProjectVersionOut])
def list_versions(project_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectVersion).filter(ProjectVersion.project_id == project_id).all()

@router.put('/{project_id}/draft', response_model=ProjectVersionOut)
def update_draft(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(status_code=403, detail='Only creators can edit projects')
    version = _get_latest_draft(db, project_id)
    if not version:
        raise HTTPException(status_code=400, detail='No editable draft found. Create a new version first.')

    version.project_name = payload.project_name
    version.project_start_date = payload.project_start_date
    version.project_end_date = payload.project_end_date
    version.business_unit = payload.business_unit
    version.reviewer_id = payload.reviewer_id
    version.creator_id = user.user_id

    record_audit(db, 'project_version', str(version.id), 'update', user.user_id, payload.model_dump())
    db.commit()
    db.refresh(version)
    return version

@router.post('/{project_id}/new-version', response_model=ProjectVersionOut)
def create_new_version(
    project_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(status_code=403, detail='Only creators can create new versions')
    project = db.get(Project, project_id)
    if not project or not project.active_version_id:
        raise HTTPException(status_code=400, detail='Project has no active version to copy')
    active = db.get(ProjectVersion, project.active_version_id)
    latest_number = (
        db.query(ProjectVersion.version_number)
        .filter(ProjectVersion.project_id == project_id)
        .order_by(ProjectVersion.version_number.desc())
        .first()[0]
    )
    version = ProjectVersion(
        project_id=project_id,
        version_number=latest_number + 1,
        status=ProjectStatus.draft.value,
        project_name=active.project_name,
        project_start_date=active.project_start_date,
        project_end_date=active.project_end_date,
        business_unit=active.business_unit,
        reviewer_id=active.reviewer_id,
        creator_id=user.user_id,
        is_active=False,
    )
    db.add(version)
    record_audit(db, 'project_version', str(version.id), 'create_new_version', user.user_id, {'from': active.id})
    db.commit()
    db.refresh(version)
    return version

@router.post('/{project_id}/submit', response_model=ProjectVersionOut)
def submit_for_approval(
    project_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(status_code=403, detail='Only creators can submit projects')
    version = _get_latest_draft(db, project_id)
    if not version:
        raise HTTPException(status_code=400, detail='No draft to submit')

    contracts = db.query(ContractDocument).filter(ContractDocument.project_version_id == version.id).count()
    categories = db.query(JobCategory).filter(JobCategory.project_version_id == version.id).count()
    if contracts == 0:
        raise HTTPException(status_code=400, detail='At least one contract document is required')
    if categories == 0:
        raise HTTPException(status_code=400, detail='At least one job category is required')

    version.status = ProjectStatus.pending.value
    version.submitted_at = datetime.utcnow()
    record_audit(db, 'project_version', str(version.id), 'submit', user.user_id, None)
    db.commit()
    db.refresh(version)
    return version

@router.post('/{project_id}/versions/{version_id}/contracts', response_model=ContractOut)
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
        raise HTTPException(status_code=403, detail='Only creators can upload contracts')

    data = file.file.read()
    key = f'{project_id}/{version_id}/{file.filename}'
    storage.save(key, data)

    contract = ContractDocument(
        project_version_id=version_id,
        document_type=document_type,
        valid_from=date.fromisoformat(valid_from),
        valid_till=date.fromisoformat(valid_till),
        s3_key=key,
        filename=file.filename,
        uploaded_at=datetime.utcnow(),
    )
    db.add(contract)
    record_audit(db, 'contract', str(contract.id), 'upload', user.user_id, {'filename': file.filename})
    db.commit()
    db.refresh(contract)
    return contract

@router.post('/{project_id}/versions/{version_id}/job-categories', response_model=list[JobCategoryOut])
def add_job_categories(
    project_id: int,
    version_id: int,
    payload: list[JobCategoryCreate],
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role != ROLE_CREATOR:
        raise HTTPException(status_code=403, detail='Only creators can add job categories')
    created = []
    for item in payload:
        jc = JobCategory(project_version_id=version_id, name=item.name, rate_card_id=item.rate_card_id)
        db.add(jc)
        created.append(jc)
    record_audit(db, 'job_category', str(version_id), 'add', user.user_id, {'count': len(created)})
    db.commit()
    return created
