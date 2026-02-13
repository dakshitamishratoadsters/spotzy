import uuid
from datetime import datetime
from typing import List, Optional,TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql as pg
if TYPE_CHECKING:
  from src.db.models.booking import Booking
  from src.db.models.parkinglot import ParkingLot


# ===================== PARKING SLOT =====================
class ParkingSlot(SQLModel, table=True):
    __tablename__ = "parking_slots"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    slot_number: str = Field(nullable=False, index=True)
    is_available: bool = Field(default=True)

    parking_lot_id: uuid.UUID = Field(
        foreign_key="parking_lots.uid",
        nullable=False
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    parking_lot: Optional["ParkingLot"] = Relationship(
        back_populates="slots",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    bookings: List["Booking"] = Relationship(
        back_populates="slot",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

