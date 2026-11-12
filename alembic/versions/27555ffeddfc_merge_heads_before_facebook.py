"""merge_heads_before_facebook

Revision ID: 27555ffeddfc
Revises: 7ccb1d80a35b, b7c12d34e56f
Create Date: 2026-11-12 10:18:46.477515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27555ffeddfc'
down_revision: Union[str, Sequence[str], None] = ('7ccb1d80a35b', 'b7c12d34e56f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
