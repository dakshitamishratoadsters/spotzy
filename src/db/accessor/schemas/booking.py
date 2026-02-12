from sqlmodel import BaseModel
from uuid import UUID
from datetime import datetime
# ---------- BOOKING ----------
class BookingCreate(BaseModel):
    slot_id: UUID
    start_time: datetime
    end_time: datetime


class BookingResponse(BaseModel):
    id: UUID
    slot_id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    amount:float

    class Config:
        from_attributes = True
