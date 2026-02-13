from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from datetime import datetime

from src.db.models.booking import Booking
from src.db.models.parkingslot import ParkingSlot
from src.db.accessor.schemas import BookingCreate


class BookingService:

    # ======================= CREATE BOOKING =======================

    async def create_booking(
        self,
        booking_data: BookingCreate,
        session: AsyncSession
    ) -> Booking:

        if booking_data.start_time >= booking_data.end_time:
            raise ValueError("start_time must be less than end_time")

        # 🔒 lock slot row (prevents double booking)
        await session.exec(
            select(ParkingSlot)
            .where(ParkingSlot.uid == booking_data.slot_id)
            .with_for_update()
        )

        # check slot exists
        slot = await session.get(ParkingSlot, booking_data.slot_id)
        if not slot:
            raise ValueError("Parking slot not found")

        # check overlapping bookings (time-based)
        overlap_stmt = select(Booking).where(
            Booking.slot_id == booking_data.slot_id,
            Booking.start_time < booking_data.end_time,
            Booking.end_time > booking_data.start_time,
            Booking.status == "BOOKED"
        )

        overlap = (await session.exec(overlap_stmt)).first()
        if overlap:
            raise ValueError("Slot already booked for this time")

        booking = Booking(
            user_id=booking_data.user_id,
            slot_id=booking_data.slot_id,
            parking_lot_id=slot.parking_lot_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            status="BOOKED"
        )

        session.add(booking)
        await session.commit()
        await session.refresh(booking)

        return booking

    # ======================= GET BOOKINGS =======================

    async def get_booking_by_uid(
        self,
        booking_uid: UUID,
        session: AsyncSession
    ) -> Booking | None:
        return await session.get(Booking, booking_uid)

    async def get_user_bookings(
        self,
        user_id: UUID,
        session: AsyncSession
    ):
        statement = select(Booking).where(Booking.user_id == user_id)
        result = await session.exec(statement)
        return result.all()

    async def get_parking_lot_bookings(
        self,
        parking_lot_id: UUID,
        session: AsyncSession
    ):
        statement = select(Booking).where(
            Booking.parking_lot_id == parking_lot_id
        )
        result = await session.exec(statement)
        return result.all()

    # ======================= CANCEL BOOKING =======================

    async def cancel_booking(
        self,
        booking_uid: UUID,
        user_id: UUID,
        session: AsyncSession
    ) -> Booking | None:

        booking = await session.get(Booking, booking_uid)
        if not booking:
            return None

        # 🔐 ownership check
        if booking.user_id != user_id:
            raise PermissionError("You cannot cancel this booking")

        booking.stat
