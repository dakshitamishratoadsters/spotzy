import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql as pg
from src.db.models.user import User
from src.db.models.parkingslot import ParkingSlot


# ===================== PARKING LOT =====================
class ParkingLot(SQLModel, table=True):
    __tablename__ = "parking_lots"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True)
    )

    name: str = Field(nullable=False)
    address: str = Field(nullable=False)
    latitude: float
    longitude: float
    total_slots: int = Field(nullable=False)

    admin_id: uuid.UUID = Field(
        foreign_key="users.uid",
        nullable=False
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    admin: Optional["User"] = Relationship(
        back_populates="parking_lots",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    slots: List["ParkingSlot"] = Relationship(
        back_populates="parking_lot",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

