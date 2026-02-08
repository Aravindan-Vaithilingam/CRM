from sqlalchemy import Column, String, Integer
from app.db.base import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
