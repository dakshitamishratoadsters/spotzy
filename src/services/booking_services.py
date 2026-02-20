from uuid import UUID
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models.booking import Booking, BookingStatus
from src.db.models.parkingslot import ParkingSlot
from src.db.accessor.schemas.booking import BookingCreate


class BookingService:

    # ======================= CREATE BOOKING =======================

    async def create_booking(
        self,
        booking_data: BookingCreate,
        user_id: UUID,
        session: AsyncSession
    ) -> Booking:

        # ⛔ time validation
        if booking_data.start_time >= booking_data.end_time:
            raise ValueError("start_time must be before end_time")

        # 🔒 lock parking slot row (prevents race conditions)
        slot_stmt = (
            select(ParkingSlot)
            .where(ParkingSlot.uid == booking_data.slot_id)
            .with_for_update()
        )
        slot = (await session.execute(slot_stmt)).one_or_none()

        if not slot:
            raise ValueError("Parking slot not found")

        # ⏱ overlap check
        overlap_stmt = select(Booking).where(
            Booking.slot_id == booking_data.slot_id,
            Booking.start_time < booking_data.end_time,
            Booking.end_time > booking_data.start_time,
            Booking.status == BookingStatus.BOOKED,
        )

        overlap = (await session.execute(overlap_stmt)).first()
        if overlap:
            raise ValueError("Slot already booked for this time")

        # ✅ create booking
        booking = Booking(
            user_id=user_id,
            slot_id=booking_data.slot_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            status=BookingStatus.BOOKED,
        )

        session.add(booking)
        await session.commit()
        await session.refresh(booking)

        return booking

    # ======================= GET SINGLE BOOKING =======================

    async def get_booking_by_uid(
        self,
        booking_uid: UUID,
        session: AsyncSession
    ) -> Booking | None:
        return await session.get(Booking, booking_uid)

    # ======================= USER BOOKINGS =======================

    async def get_user_bookings(
        self,
        user_id: UUID,
        session: AsyncSession
    ):
        stmt = select(Booking).where(Booking.user_id == user_id)
        result = await session.exec(stmt)
        return result.all()

    # ======================= SLOT BOOKINGS (ADMIN) =======================

    async def get_slot_bookings(
        self,
        slot_id: UUID,
        session: AsyncSession
    ):
        stmt = select(Booking).where(Booking.slot_id == slot_id)
        result = await session.exec(stmt)
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

        # 🚫 already cancelled/completed
        if booking.status != BookingStatus.BOOKED:
            raise ValueError("Only active bookings can be cancelled")

        booking.status = BookingStatus.CANCELLED

        await session.commit()
        await session.refresh(booking)

        return booking


booking_service = BookingService()