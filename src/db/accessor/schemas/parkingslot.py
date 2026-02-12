from sqlmodel import BaseModel
from uuid import UUID
# ---------- PARKING SLOT ----------
class SlotCreate(BaseModel):
    slot_number: str


class SlotResponse(BaseModel):
    id: UUID
    slot_number: str
    is_available: bool

    class Config:
        from_attributes = True
