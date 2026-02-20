from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from src.db.models.booking import BookingStatus


# ===================== BOOKING CREATE =====================
class BookingCreate(BaseModel):
    slot_id: UUID
    start_time: datetime
    end_time: datetime


# ===================== BOOKING RESPONSE =====================
class BookingResponse(BaseModel):
    uid: UUID
    user_id: UUID
    slot_id: UUID
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True