"""merge heads

Revision ID: 3995dfe1a7d0
Revises: 15011899361c, c2422295b416
Create Date: 2026-02-23 16:42:45.739424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3995dfe1a7d0'
down_revision: Union[str, Sequence[str], None] = ('15011899361c', 'c2422295b416')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
