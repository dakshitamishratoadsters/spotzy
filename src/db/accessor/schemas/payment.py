from sqlmodel import BaseModel
from uuid import UUID

# ---------- PAYMENT ----------
class PaymentCreate(BaseModel):
    booking_id: UUID
    amount: float
    payment_method: str