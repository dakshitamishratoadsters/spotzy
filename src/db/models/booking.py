import uuid
from datetime import datetime
from typing import List, Optional ,TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum
from sqlalchemy.dialects import postgresql as pg
from enum import Enum
if TYPE_CHECKING:
  from src.db.models.user import User 
  from src.db.models.parkingslot import ParkingSlot
  from src.db.models.payment import Payment
  

class BookingStatus(str, Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"




# ===================== BOOKING =====================
class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    start_time: datetime
    end_time: datetime

    status: BookingStatus = Field(
    sa_column=Column(
        pg.VARCHAR,
        nullable=False,
        server_default=BookingStatus.BOOKED.value)
    )

    user_id: uuid.UUID = Field(
        foreign_key="users.uid",
        nullable=False
    )

    slot_id: uuid.UUID = Field(
        foreign_key="parking_slots.uid",
        nullable=False
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    user: Optional["User"] = Relationship(
        back_populates="bookings",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    slot: Optional["ParkingSlot"] = Relationship(
        back_populates="bookings",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    payment: Optional["Payment"] = Relationship(
        back_populates="booking",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
