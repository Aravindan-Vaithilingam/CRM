from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from app.db.base import Base

class ApprovalEvent(Base):
    __tablename__ = 'approval_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_version_id = Column(Integer, ForeignKey('project_versions.id'), nullable=False)
    action = Column(String)
    actor_id = Column(Integer, ForeignKey('users.id'))
    comment = Column(String)
    created_at = Column(DateTime)