import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

if TYPE_CHECKING:
    from src.db.models.booking import Booking

from enum import Enum

class PaymentStatus(str, Enum):
    created = "created"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )

    booking_id: uuid.UUID = Field(
        foreign_key="bookings.uid",
        nullable=False,
        index=True,
    )

    # 🔐 Razorpay fields
    razorpay_order_id: str = Field(nullable=False, index=True)
    razorpay_payment_id: Optional[str] = Field(default=None, index=True)
    razorpay_signature: Optional[str] = Field(default=None)

    amount: float = Field(nullable=False)
    currency: str = Field(default="INR", max_length=10)

    status: PaymentStatus = Field(
        sa_column=Column(
            "status",
            nullable=False,
        ),
        default=PaymentStatus.created,
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    # 🔗 Relationships
    booking: Optional["Booking"] = Relationship(back_populates="payment")