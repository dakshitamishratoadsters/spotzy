from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.api.v1.dependencies import get_current_user
from src.db.database import get_session

from src.db.models.user import User
from src.db.models.booking import Booking, BookingStatus
from src.db.models.payment import Payment, PaymentStatus

from src.services.payment_services import payment_service
from src.db.accessor.schemas.payment import (
    PaymentCreate,
    RazorpayOrderResponse,
    PaymentResponse,
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)

# =====================================================
# CREATE PAYMENT ORDER (Pay Now)
# =====================================================
@router.post(
    "/create-order",
    response_model=RazorpayOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_order(
    payload: PaymentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1️⃣ Fetch booking
    booking = await session.get(Booking, payload.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # 2️⃣ Ownership check
    if booking.user_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your booking",
        )

    # 3️⃣ Booking must be waiting for payment
    if booking.status != BookingStatus.PAYMENT_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment not allowed for this booking status",
        )

    # 4️⃣ Prevent duplicate successful payment
    result = await session.execute(
        select(Payment).where(
            Payment.booking_id == booking.uid,
            Payment.status == PaymentStatus.paid,
        )
    )
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already completed for this booking",
        )

    # 5️⃣ Create Razorpay order
    payment = await payment_service.create_payment_order(
        booking_id=payload.booking_id,
        amount=payload.amount,
        currency=payload.currency,
        session=session,
    )

    return {
        "payment_id": payment.uid,
        "razorpay_order_id": payment.razorpay_order_id,
        "amount": payment.amount,
        "currency": payment.currency,
    }


# =====================================================
# GET PAYMENT BY BOOKING ID
# =====================================================
@router.get(
    "/booking/{booking_id}",
    response_model=PaymentResponse,
)
async def get_payment_by_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Payment).where(Payment.booking_id == booking_id)
    )
    payment = result.scalars().first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this booking",
        )

    booking = await session.get(Booking, payment.booking_id)
    if booking.user_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    return payment


# =====================================================
# GET PAYMENT BY PAYMENT ID
# =====================================================
@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
async def get_payment_by_id(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    payment = await session.get(Payment, payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    booking = await session.get(Booking, payment.booking_id)
    if booking.user_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed",
        )

    return payment