"""drop payments table

Revision ID: ccd4bf2155a6
Revises: 0ff70c14f58d
Create Date: 2026-02-23 13:19:00.246783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccd4bf2155a6'
down_revision: Union[str, Sequence[str], None] = '0ff70c14f58d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # drop table first (because enum may be referenced)
    op.drop_table("payments")

    # drop enum if it exists
    op.execute("DROP TYPE IF EXISTS paymentstatus CASCADE")


def downgrade() -> None:
    # usually we keep downgrade empty or recreate if needed
    pass
