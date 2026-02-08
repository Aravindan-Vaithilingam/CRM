from sqlalchemy import Column, String, Boolean, Integer
from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # basic client info
    legal_entity_name = Column(String, nullable=False)
    registered_address = Column(String, nullable=False)
    billing_address = Column(String, nullable=True)
    billing_same_as_registered = Column(Boolean, default=True)

    mode_of_payment = Column(String, nullable=False)
    gst_number = Column(String, nullable=False)
    billing_currency = Column(String, nullable=False)

    primary_contact_name = Column(String, nullable=False)
    primary_contact_designation = Column(String, nullable=True)
    primary_contact_phone = Column(String, nullable=False)
    primary_contact_email = Column(String, nullable=False)