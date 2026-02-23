"""booking

Revision ID: 76909c29c6ed
Revises: 9640eb578dd9
Create Date: 2026-02-20 16:04:25.429106
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "76909c29c6ed"
down_revision: Union[str, Sequence[str], None] = "9640eb578dd9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1️⃣ Create ENUM type
    booking_status_enum = postgresql.ENUM(
        "BOOKED",
        "CANCELLED",
        "COMPLETED",
        name="booking_status",
    )
    booking_status_enum.create(op.get_bind(), checkfirst=True)

    # 2️⃣ DROP DEFAULT FIRST (CRITICAL)
    op.alter_column(
        "bookings",
        "status",
        server_default=None,
    )

    # 3️⃣ Convert VARCHAR → ENUM with explicit cast
    op.alter_column(
        "bookings",
        "status",
        existing_type=sa.VARCHAR(),
        type_=booking_status_enum,
        existing_nullable=False,
        postgresql_using="status::booking_status",
    )

    # 4️⃣ SET DEFAULT AGAIN (as ENUM)
    op.alter_column(
        "bookings",
        "status",
        server_default=sa.text("'BOOKED'"),
    )

    # 5️⃣ Make timestamps timezone-aware
    op.alter_column(
        "bookings",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )

    op.alter_column(
        "bookings",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )

def downgrade() -> None:
    # 1️⃣ DROP ENUM DEFAULT
    op.alter_column(
        "bookings",
        "status",
        server_default=None,
    )

    # 2️⃣ Convert ENUM → VARCHAR
    op.alter_column(
        "bookings",
        "status",
        existing_type=postgresql.ENUM(
            "BOOKED",
            "CANCELLED",
            "COMPLETED",
            name="booking_status",
        ),
        type_=sa.VARCHAR(),
        existing_nullable=False,
    )

    # 3️⃣ Restore VARCHAR default
    op.alter_column(
        "bookings",
        "status",
        server_default=sa.text("'BOOKED'::character varying"),
    )

    # 4️⃣ Revert timestamps
    op.alter_column(
        "bookings",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=True,
    )

    op.alter_column(
        "bookings",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=True,
    )

    # 5️⃣ Drop ENUM type
    booking_status_enum = postgresql.ENUM(
        "BOOKED",
        "CANCELLED",
        "COMPLETED",
        name="booking_status",
    )
    booking_status_enum.drop(op.get_bind(), checkfirst=True)