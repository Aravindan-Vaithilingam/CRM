from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    role: str


class UserOut(BaseModel):
    id: int
    name: str
    role: str

    class Config:
        from_attributes = True
