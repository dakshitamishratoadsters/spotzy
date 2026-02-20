from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from src.db.database import get_session
from src.api.v1.dependencies import get_current_user
from src.db.models.user import User
from src.services.booking_services import booking_service
from src.db.accessor.schemas.booking import BookingCreate, BookingResponse
from src.db.models.booking import Booking, BookingStatus

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# =========================
# Admin Helper
# =========================
def ensure_admin(user: User):
    if user.role != "admin":  # or user.is_admin if you use that
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


# =========================
# Create Booking (USER)
# =========================
@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_data: BookingCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        return await booking_service.create_booking(
            booking_data=booking_data,
            user_id=current_user.uid,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =========================
# Get My Bookings (USER)
# =========================
@router.get(
    "/my",
    response_model=list[BookingResponse],
)
async def get_my_bookings(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.get_user_bookings(
        user_id=current_user.uid,
        session=session,
    )


# =========================
# Get Booking by ID (USER / ADMIN)
# =========================
@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def get_booking_by_id(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    booking = await booking_service.get_booking_by_uid(
        booking_uid=booking_id,
        session=session,
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.user_id != current_user.uid and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this booking",
        )

    return booking


# =========================
# Cancel Booking (USER)
# =========================
@router.delete(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def cancel_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = await booking_service.cancel_booking(
            booking_uid=booking_id,
            user_id=current_user.uid,
            session=session,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


# =========================
# Get All Bookings (ADMIN)
# =========================
@router.get(
    "",
    response_model=list[BookingResponse],
)
async def get_all_bookings(
    status: BookingStatus | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    stmt = select(Booking)
    if status:
        stmt = stmt.where(Booking.status == status)

    result = await session.exec(stmt)
    return result.all()


# =========================
# Get Slot Bookings (ADMIN)
# =========================
@router.get(
    "/slots/{slot_id}",
    response_model=list[BookingResponse],
)
async def get_slot_bookings(
    slot_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    return await booking_service.get_slot_bookings(
        slot_id=slot_id,
        session=session,
    )


# =========================
# Update Booking Status (ADMIN)
# =========================
class BookingStatusUpdate(BaseModel):
    status: BookingStatus


@router.patch(
    "/{booking_id}/status",
    response_model=BookingResponse,
)
async def update_booking_status(
    booking_id: UUID,
    data: BookingStatusUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    booking.status = data.status
    await session.commit()
    await session.refresh(booking)

    return booking