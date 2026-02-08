from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut
from app.models.user import User

router = APIRouter()


@router.post('', response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get('', response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
