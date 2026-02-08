from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.client import ClientCreate, ClientOut
from app.models.client import Client

router = APIRouter()


@router.post("", response_model=ClientOut)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
):
    # handle
    client_data = payload.model_dump()
    client = Client(**client_data)

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@router.get("", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db)):
    # keep  this simple; add pagination later
    return db.query(Client).all()


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
):
    client = db.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    return client
