import uuid
from datetime import datetime
from typing import List, Optional,TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql as pg
if TYPE_CHECKING:
  from src.db.models.booking import Booking

# ===================== PAYMENT =====================
class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    amount: float = Field(nullable=False)

    payment_status: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="PENDING")
    )

    payment_method: str = Field(nullable=False)

    booking_id: uuid.UUID = Field(
        foreign_key="bookings.uid",
        nullable=False,
        unique=True
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    booking: Optional["Booking"] = Relationship(
        back_populates="payment",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
