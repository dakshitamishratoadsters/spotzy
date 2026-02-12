import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql as pg
from src.db.models.booking import Booking
from src.db.models.parkinglot import ParkingLot


# ===================== USER =====================
class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            unique=True,
            nullable=False
        )
    )

    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(nullable=False, unique=True, index=True)
    email: str = Field(nullable=False, unique=True, index=True)
    password_hash: str = Field(nullable=False)

    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    bookings: List["Booking"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    parking_lots: List["ParkingLot"] = Relationship(
        back_populates="admin",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
