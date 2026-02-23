"""create payment table

Revision ID: c2422295b416
Revises: ccd4bf2155a6
Create Date: 2026-02-23 13:20:35.868257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c2422295b416'
down_revision: Union[str, Sequence[str], None] = 'ccd4bf2155a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()

    payment_status_enum_create = postgresql.ENUM(
        "created",
        "paid",
        "failed",
        "refunded",
        name="payment_status_enum",
    )
    payment_status_enum_create.create(bind, checkfirst=True)

    payment_status_enum = postgresql.ENUM(
        "created",
        "paid",
        "failed",
        "refunded",
        name="payment_status_enum",
        create_type=False,
    )

    op.create_table(
        "payments",
        sa.Column("uid", sa.UUID(), primary_key=True),
        sa.Column("booking_id", sa.UUID(), nullable=False),
        sa.Column("razorpay_order_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("razorpay_payment_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("razorpay_signature", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
        sa.Column("status", payment_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.uid"]),
    )

    op.create_index("ix_payments_booking_id", "payments", ["booking_id"])
    op.create_index("ix_payments_razorpay_order_id", "payments", ["razorpay_order_id"])
    op.create_index("ix_payments_razorpay_payment_id", "payments", ["razorpay_payment_id"])

def downgrade() -> None:
    op.drop_index("ix_payments_razorpay_payment_id", table_name="payments")
    op.drop_index("ix_payments_razorpay_order_id", table_name="payments")
    op.drop_index("ix_payments_booking_id", table_name="payments")

    op.drop_table("payments")

    op.execute("DROP TYPE IF EXISTS public.payment_status_enum CASCADE")