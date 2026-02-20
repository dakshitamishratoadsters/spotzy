from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from uuid import UUID
from datetime import datetime

from starlette.exceptions import HTTPException

from src.db.models.parkinglot import ParkingLot
from src.db.models.parkingslot import ParkingSlot
from src.db.models.booking import Booking
from src.db.accessor.schemas.parkinglot import ParkingLotCreate
from src.db.accessor.schemas.parkingslot import  SlotCreate


class ParkingService:

    # ======================= PARKING LOT =======================

    async def create_parking_lot(
        self,
        parking_data: ParkingLotCreate,
        session: AsyncSession,
        admin_id:UUID
    ) -> ParkingLot:
        parking_lot = ParkingLot(**parking_data.model_dump(), admin_id=admin_id)

        session.add(parking_lot)
        await session.commit()
        await session.refresh(parking_lot)

        return parking_lot

    async def get_all_parking_lots(
        self,
        session: AsyncSession
    ):
        result = await session.execute(select(ParkingLot))
        return result.scalars().all()

    async def get_parking_lot_by_uid(
        self,
        parking_lot_id: UUID,
        session: AsyncSession
    ) -> ParkingLot | None:
        return await session.get(ParkingLot, parking_lot_id)

    async def search_parking_lots(
        self,
        query: str,
        session: AsyncSession
    ):
        statement = select(ParkingLot).where(
            ParkingLot.name.ilike(f"%{query}%") |
            ParkingLot.address.ilike(f"%{query}%")
        )
        result = await session.execute(statement)
        return result.scalars().all()


parking_service=ParkingService()