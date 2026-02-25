"""extend booking status enum for payment flow

Revision ID: 872a43bdaf89
Revises: c2422295b416
Create Date: 2026-02-24 15:42:09.833034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '872a43bdaf89'
down_revision: Union[str, Sequence[str], None] = 'c2422295b416'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE booking_status ADD VALUE IF NOT EXISTS 'PAYMENT_PENDING'")
    op.execute("ALTER TYPE booking_status ADD VALUE IF NOT EXISTS 'CONFIRMED'")
    op.execute("ALTER TYPE booking_status ADD VALUE IF NOT EXISTS 'PAYMENT_FAILED'")




def downgrade() -> None:
    """Downgrade schema."""
    pass
