from sqlmodel import BaseModel
from uuid import UUID

# ---------- PARKING LOT ----------
class ParkingLotCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    total_slots: int


class ParkingLotResponse(BaseModel):
    id: UUID
    name: str
    address: str
    latitude: float
    longitude: float
    total_slots: int

    class Config:
        from_attributes = True
