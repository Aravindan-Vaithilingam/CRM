from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    legal_entity_name: str
    registered_address: str
    billing_address: str | None = None
    billing_same_as_registered: bool = True
    mode_of_payment: str
    gst_number: str
    billing_currency: str
    primary_contact_name: str
    primary_contact_designation: str | None = None
    primary_contact_phone: str
    primary_contact_email: EmailStr

class ClientCreate(ClientBase):
    pass

class ClientOut(ClientBase):
    id: int

    class Config:
        from_attributes = True
