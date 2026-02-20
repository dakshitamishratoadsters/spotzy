from uuid import UUID
from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.db.models.parkingslot import ParkingSlot
from src.db.models.parkinglot import ParkingLot
from src.db.models.user import User
from src.db.accessor.schemas.parkingslot import SlotCreate, SlotUpdate


class ParkingSlotService:

    # ===================== CREATE SLOT (ADMIN ONLY) =====================
    async def create_slot(
        self,
        parking_lot_id: UUID,
        slot_data: SlotCreate,
        session: AsyncSession,
        current_user: User
    ) -> ParkingSlot:

        if current_user.role != "ADMIN":
            raise PermissionError("Only admin can create parking slots")

        parking_lot = await session.get(ParkingLot, parking_lot_id)
        if not parking_lot:
            raise ValueError("Parking lot not found")

        slot = ParkingSlot(
            slot_number=slot_data.slot_number,
            parking_lot_id=parking_lot_id,
            is_available=True
        )

        session.add(slot)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Slot number already exists in this parking lot")

        await session.refresh(slot)
        return slot

    # ===================== GET ALL SLOTS BY PARKING LOT (USER ACCESS) =====================
    async def get_slots_by_parking_lot(
        self,
        parking_lot_id: UUID,
        session: AsyncSession
    ) -> List[ParkingSlot]:

        stmt = select(ParkingSlot).where(
            ParkingSlot.parking_lot_id == parking_lot_id
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    # ===================== GET SLOT BY ID (USER ACCESS) =====================
    async def get_slot_by_id(
        self,
        slot_id: UUID,
        session: AsyncSession
    ) -> ParkingSlot | None:

        return await session.get(ParkingSlot, slot_id)

    # ===================== UPDATE SLOT (ADMIN ONLY) =====================
    async def update_slot(
        self,
        slot_id: UUID,
        slot_data: SlotUpdate,
        session: AsyncSession,
        current_user: User
    ) -> ParkingSlot:

        if current_user.role != "ADMIN":
            raise PermissionError("Only admin can update parking slots")

        slot = await session.get(ParkingSlot, slot_id)
        if not slot:
            raise ValueError("Parking slot not found")

        if slot_data.slot_number is not None:
            slot.slot_number = slot_data.slot_number

        if slot_data.is_available is not None:
            slot.is_available = slot_data.is_available

        session.add(slot)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("Slot number already exists in this parking lot")

        await session.refresh(slot)
        return slot


parking_slot_service = ParkingSlotService()