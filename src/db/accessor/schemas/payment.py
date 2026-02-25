from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# =========================
# PAYMENT STATUS ENUM
# =========================
class PaymentStatus(str, Enum):
    created = "created"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


# =========================
# CREATE PAYMENT (REQUEST)
# =========================
# Used when user clicks "Pay Now"
class PaymentCreate(BaseModel):
    booking_id: UUID
    amount: float = Field(..., gt=0)
    currency: str = "INR"


# =========================
# RAZORPAY ORDER RESPONSE
# =========================
# Sent from backend → frontend
class RazorpayOrderResponse(BaseModel):
    payment_id: UUID
    razorpay_order_id: str
    amount: float
    currency: str


# =========================
# PAYMENT RESPONSE (READ)
# =========================
# Used for GET APIs
class PaymentResponse(BaseModel):
    uid: UUID
    booking_id: UUID

    razorpay_order_id: str
    razorpay_payment_id: str | None

    amount: float
    currency: str
    status: PaymentStatus

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True