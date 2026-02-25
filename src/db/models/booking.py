import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects import postgresql as pg

if TYPE_CHECKING:
    from src.db.models.user import User
    from src.db.models.parkingslot import ParkingSlot
    from src.db.models.payment import Payment


class BookingStatus(str, Enum):
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    BOOKED = "BOOKED"  # legacy (keep for DB compatibility)


# ===================== BOOKING =====================
class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True),
    )

    start_time: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    end_time: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    status: BookingStatus = Field(
        sa_column=Column(
            pg.ENUM(
                BookingStatus,
                name="booking_status",
                create_type=False,
            ),
            nullable=False,
        ),
        default=BookingStatus.PAYMENT_PENDING,
    )

    user_id: uuid.UUID = Field(
        foreign_key="users.uid",
        nullable=False,
    )

    slot_id: uuid.UUID = Field(
        foreign_key="parking_slots.uid",
        nullable=False,
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )

    user: Optional["User"] = Relationship(back_populates="bookings")
    slot: Optional["ParkingSlot"] = Relationship(back_populates="bookings")
    payment: Optional["Payment"] = Relationship(back_populates="booking")