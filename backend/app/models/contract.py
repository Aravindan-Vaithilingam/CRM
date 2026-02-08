from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class ContractDocument(Base):
    __tablename__ = 'contract_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_version_id = Column(Integer, ForeignKey('project_versions.id'), nullable=False)
    document_type = Column(String, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_till = Column(Date, nullable=False)
    s3_key = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

    project_version = relationship('ProjectVersion', back_populates='contracts')
