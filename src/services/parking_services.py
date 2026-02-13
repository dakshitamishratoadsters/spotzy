from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from uuid import UUID
from datetime import datetime

from src.db.models.parkinglot import ParkingLot
from src.db.models.parkingslot import ParkingSlot
from src.db.models.booking import Booking
from src.db.accessor.schemas import ParkingLotCreate, SlotCreate


class ParkingService:

    # ======================= PARKING LOT =======================

    async def create_parking_lot(
        self,
        parking_data: ParkingLotCreate,
        session: AsyncSession
    ) -> ParkingLot:
        parking_lot = ParkingLot(**parking_data.model_dump())

        session.add(parking_lot)
        await session.commit()
        await session.refresh(parking_lot)

        return parking_lot

    async def get_all_parking_lots(
        self,
        session: AsyncSession
    ):
        result = await session.exec(select(ParkingLot))
        return result.all()

    async def get_parking_lot_by_uid(
        self,
        parking_lot_uid: UUID,
        session: AsyncSession
    ) -> ParkingLot | None:
        return await session.get(ParkingLot, parking_lot_uid)

    async def search_parking_lots(
        self,
        query: str,
        session: AsyncSession
    ):
        statement = select(ParkingLot).where(
            ParkingLot.name.ilike(f"%{query}%") |
            ParkingLot.address.ilike(f"%{query}%")
        )
        result = await session.exec(statement)
        return result.all()

    # ======================= SLOTS =======================

    async def create_parking_slot(
        self,
        parking_lot_uid: UUID,
        slot_data: SlotCreate,
        session: AsyncSession
    ) -> ParkingSlot:

        slot = ParkingSlot(
            slot_number=slot_data.slot_number,
            parking_lot_id=parking_lot_uid
        )

        session.add(slot)
        await session.commit()
        await session.refresh(slot)

        # update counts only
        await self.update_parking_lot_availability(
            parking_lot_uid,
            session
        )

        return slot

    async def get_slots_by_parking_lot(
        self,
        parking_lot_uid: UUID,
        session: AsyncSession
    ):
        statement = select(ParkingSlot).where(
            ParkingSlot.parking_lot_id == parking_lot_uid
        )
        result = await session.exec(statement)
        return result.all()

    async def get_slot_by_uid(
        self,
        slot_uid: UUID,
        session: AsyncSession
    ) -> ParkingSlot | None:
        return await session.get(ParkingSlot, slot_uid)

    # ======================= AVAILABILITY (TIME BASED) =======================

    async def get_available_slots(
        self,
        parking_lot_uid: UUID,
        start_time: datetime,
        end_time: datetime,
        session: AsyncSession
    ):
        if start_time >= end_time:
            raise ValueError("start_time must be less than end_time")

        # fetch all slots of the parking lot
        slot_stmt = select(ParkingSlot).where(
            ParkingSlot.parking_lot_id == parking_lot_uid
        )
        slots = (await session.exec(slot_stmt)).all()

        if not slots:
            return []

        slot_ids = [slot.uid for slot in slots]

        # fetch overlapping bookings
        booking_stmt = select(Booking).where(
            Booking.slot_id.in_(slot_ids),
            Booking.start_time < end_time,
            Booking.end_time > start_time,
            Booking.status == "BOOKED"
        )
        bookings = (await session.exec(booking_stmt)).all()

        booked_slot_ids = {booking.slot_id for booking in bookings}

        # return only free slots for this time window
        return [
            slot for slot in slots
            if slot.uid not in booked_slot_ids
        ]

    # ======================= UPDATE PARKING LOT COUNTS =======================

    async def update_parking_lot_availability(
        self,
        parking_lot_uid: UUID,
        session: AsyncSession
    ) -> ParkingLot | None:

        parking_lot = await session.get(ParkingLot, parking_lot_uid)
        if not parking_lot:
            return None

        # total slots
        total_slots_stmt = select(func.count(ParkingSlot.uid)).where(
            ParkingSlot.parking_lot_id == parking_lot_uid
        )
        total_slots = (await session.exec(total_slots_stmt)).one()

        # currently booked slots (NOW)
        now = datetime.utcnow()

        booked_slots_stmt = select(func.count(func.distinct(Booking.slot_id))).where(
            Booking.parking_lot_id == parking_lot_uid,
            Booking.status == "BOOKED",
            Booking.start_time <= now,
            Booking.end_time >= now
        )
        booked_slots = (await session.exec(booked_slots_stmt)).one()

        parking_lot.total_slots = total_slots
        parking_lot.available_slots = total_slots - booked_slots

        session.add(parking_lot)
        await session.commit()
        await session.refresh(parking_lot)

        return parking_lot
