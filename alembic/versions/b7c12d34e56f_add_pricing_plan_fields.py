"""add pricing plan and subscription fields

Revision ID: b7c12d34e56f
Revises: 3116eeb5f011
Create Date: 2026-11-11 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c12d34e56f'
down_revision: Union[str, Sequence[str], None] = '3116eeb5f011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('plan_name', sa.String(length=50), server_default='Free', nullable=False))
    op.add_column('users', sa.Column('plan_status', sa.String(length=20), server_default='active', nullable=False))
    op.add_column('users', sa.Column('plan_duration_hours', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('plan_activated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('plan_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'plan_expires_at')
    op.drop_column('users', 'plan_activated_at')
    op.drop_column('users', 'plan_duration_hours')
    op.drop_column('users', 'plan_status')
    op.drop_column('users', 'plan_name')

