from pydantic import BaseModel, Field
from uuid import UUID

# ---------- PARKING LOT ----------
class ParkingLotCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    total_slots: int = Field(default=0)      # default total slots
    available_slots: int = Field(default=0)  # default available slots

    class Config:
        from_attributes = True


class ParkingLotResponse(BaseModel):
    uid: UUID
    name: str
    address: str
    latitude: float
    longitude: float
    total_slots: int
    available_slots: int
    admin_id: UUID

    class Config:
        from_attributes = True
