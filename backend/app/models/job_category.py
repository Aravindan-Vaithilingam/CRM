from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

class RateCard(Base):
    __tablename__ = 'rate_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    rate_per_hour = Column(String, nullable=False)
    currency = Column(String, nullable=False)

class JobCategory(Base):
    __tablename__ = 'job_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_version_id = Column(Integer, ForeignKey('project_versions.id'), nullable=False)
    name = Column(String, nullable=False)
    rate_card_id = Column(Integer, ForeignKey('rate_cards.id'), nullable=False)
    project_version = relationship('ProjectVersion', back_populates='job_categories')
    rate_card = relationship('RateCard')
