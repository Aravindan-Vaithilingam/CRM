from datetime import date, datetime
from pydantic import BaseModel
from app.models.common import ProjectStatus

class ProjectBase(BaseModel):
    project_code: str
    project_name: str
    project_start_date: date
    project_end_date: date
    business_unit: str
    reviewer_id: int

class ProjectCreate(ProjectBase):
    client_id: int

class ProjectUpdate(ProjectBase):
    pass

class ProjectVersionOut(BaseModel):
    id: int
    project_id: int
    version_number: int
    status: ProjectStatus
    project_name: str
    project_start_date: date
    project_end_date: date
    business_unit: str
    reviewer_id: int
    creator_id: int
    submitted_at: datetime | None
    approved_at: datetime | None
    rejected_at: datetime | None
    rejection_comment: str | None
    is_active: bool

    class Config:
        from_attributes = True

class ProjectOut(BaseModel):
    id: int
    project_code: str
    name: str
    client_id: int
    created_by: int
    active_version_id: int | None

    class Config:
        from_attributes = True
