from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ===================== SLOT CREATE =====================
class SlotCreate(BaseModel):
    slot_number: str = Field(..., min_length=2)


# ===================== SLOT UPDATE =====================
class SlotUpdate(BaseModel):
    slot_number: Optional[str] = Field(None, min_length=2)
    is_available: Optional[bool] = None


# ===================== SLOT RESPONSE =====================
class SlotResponse(BaseModel):
    uid: UUID
    slot_number: str
    is_available: bool
    parking_lot_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True