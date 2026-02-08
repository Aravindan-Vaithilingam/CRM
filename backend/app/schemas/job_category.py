from pydantic import BaseModel

class RateCardOut(BaseModel):
    id: int
    name: str
    rate_per_hour: str
    currency: str

class JobCategoryCreate(BaseModel):
    name: str
    rate_card_id: int

class JobCategoryOut(BaseModel):
    id: int
    project_version_id: int
    name: str
    rate_card_id: int

    class Config:
        from_attributes = True
