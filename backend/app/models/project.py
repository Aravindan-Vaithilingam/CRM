from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.common import ProjectStatus

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_code = Column(String, nullable=False, unique=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    active_version_id = Column(Integer, ForeignKey('project_versions.id'))

    client = relationship('Client')
    versions = relationship(
        'ProjectVersion',
        back_populates='project',
        foreign_keys='ProjectVersion.project_id',
    )

class ProjectVersion(Base):
    __tablename__ = 'project_versions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    status = Column(String, default=ProjectStatus.draft.value, nullable=False)

    project_name = Column(String, nullable=False)
    project_start_date = Column(Date, nullable=False)
    project_end_date = Column(Date, nullable=False)

    business_unit = Column(String, nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    rejection_comment = Column(String)
    is_active = Column(Boolean, default=False)

    project = relationship(
        'Project',
        back_populates='versions',
        foreign_keys=[project_id],
    )
    contracts = relationship('ContractDocument', back_populates='project_version')
    job_categories = relationship('JobCategory', back_populates='project_version')
