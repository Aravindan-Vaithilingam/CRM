from datetime import date, datetime
from pydantic import BaseModel

class ContractCreate(BaseModel):
    document_type: str
    valid_from: date
    valid_till: date

class ContractOut(BaseModel):
    id: int
    project_version_id: int
    document_type: str
    valid_from: date
    valid_till: date
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
