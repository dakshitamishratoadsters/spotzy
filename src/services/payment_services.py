from uuid import UUID
import razorpay

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.config import Config
from src.db.models.payment import Payment, PaymentStatus
from src.db.models.booking import Booking


# =========================
# RAZORPAY CLIENT
# =========================
razorpay_client = razorpay.Client(
    auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET)
)


# =========================
# PAYMENT SERVICE
# =========================
class PaymentService:

    # -------------------------
    # CREATE PAYMENT ORDER
    # -------------------------
    async def create_payment_order(
        self,
        booking_id: UUID,
        amount: float,
        currency: str,
        session: AsyncSession,
    ) -> Payment:

        # 1️⃣ Validate booking
        booking = await session.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )

        # 2️⃣ Create Razorpay order (amount in paise)
        order = razorpay_client.order.create(
            {
                "amount": int(amount * 100),
                "currency": currency,
                "payment_capture": 1,
            }
        )

        # 3️⃣ Save payment record
        payment = Payment(
            booking_id=booking_id,
            razorpay_order_id=order["id"],
            amount=amount,
            currency=currency,
            status=PaymentStatus.created,
        )

        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        return payment

    # -------------------------
    # VERIFY PAYMENT
    # -------------------------
    async def verify_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
        session: AsyncSession,
    ) -> Payment:

        # 1️⃣ Fetch payment record
        result = await session.exec(
            select(Payment).where(
                Payment.razorpay_order_id == razorpay_order_id
            )
        )
        payment = result.first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found",
            )

        # 2️⃣ Verify Razorpay signature
        try:
            razorpay_client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )
        except razorpay.errors.SignatureVerificationError:
            payment.status = PaymentStatus.failed
            await session.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment verification failed",
            )

        # 3️⃣ Update payment as SUCCESS
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = PaymentStatus.paid

        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        return payment


# =========================
# SERVICE INSTANCE
# =========================
payment_service = PaymentService()