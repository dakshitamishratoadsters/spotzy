from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

import json
import hmac
import hashlib

from src.db.database import get_session
from src.db.models.payment import Payment, PaymentStatus
from src.db.models.booking import Booking, BookingStatus
from src.core.config import Config

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)

# ==================================================
# VERIFY RAZORPAY WEBHOOK SIGNATURE
# ==================================================
def verify_razorpay_webhook_signature(
    body: bytes,
    signature: str,
    secret: str,
) -> bool:
    expected_signature = hmac.new(
        key=secret.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


# ==================================================
# RAZORPAY WEBHOOK ENDPOINT
# ==================================================
@router.post("/razorpay", include_in_schema=False)
async def razorpay_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    body = await request.body()

    signature = request.headers.get("X-Razorpay-Signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Razorpay signature",
        )

    if not verify_razorpay_webhook_signature(
        body=body,
        signature=signature,
        secret=Config.RAZORPAY_WEBHOOK_SECRET,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    payload = json.loads(body)
    event = payload.get("event")

    if event == "payment.captured":
        await handle_payment_captured(payload, session)

    elif event == "payment.failed":
        await handle_payment_failed(payload, session)

    elif event == "refund.processed":
        await handle_refund_processed(payload, session)

    return {"status": "ok"}


# ==================================================
# EVENT HANDLERS
# ==================================================
async def handle_payment_captured(payload: dict, session: AsyncSession):
    entity = payload["payload"]["payment"]["entity"]
    razorpay_order_id = entity["order_id"]
    razorpay_payment_id = entity["id"]

    result = await session.exec(
        select(Payment).where(
            Payment.razorpay_order_id == razorpay_order_id
        )
    )
    payment = result.first()

    # Idempotency guard
    if not payment or payment.status == PaymentStatus.paid:
        return

    # Update payment
    payment.status = PaymentStatus.paid
    payment.razorpay_payment_id = razorpay_payment_id

    # Update booking
    booking = await session.get(Booking, payment.booking_id)
    if booking and booking.status == BookingStatus.PAYMENT_PENDING:
        booking.status = BookingStatus.BOOKED

    await session.commit()


async def handle_payment_failed(payload: dict, session: AsyncSession):
    entity = payload["payload"]["payment"]["entity"]
    razorpay_order_id = entity["order_id"]

    result = await session.exec(
        select(Payment).where(
            Payment.razorpay_order_id == razorpay_order_id
        )
    )
    payment = result.first()

    if not payment or payment.status == PaymentStatus.failed:
        return

    payment.status = PaymentStatus.failed

    booking = await session.get(Booking, payment.booking_id)
    if booking and booking.status == BookingStatus.PAYMENT_PENDING:
        booking.status = BookingStatus.PAYMENT_FAILED

    await session.commit()


async def handle_refund_processed(payload: dict, session: AsyncSession):
    entity = payload["payload"]["refund"]["entity"]
    razorpay_payment_id = entity["payment_id"]

    result = await session.exec(
        select(Payment).where(
            Payment.razorpay_payment_id == razorpay_payment_id
        )
    )
    payment = result.first()

    if not payment or payment.status == PaymentStatus.refunded:
        return

    payment.status = PaymentStatus.refunded

    booking = await session.get(Booking, payment.booking_id)
    if booking:
        booking.status = BookingStatus.CANCELLED

    await session.commit()