"""add updated_at to tickets table

Revision ID: 9e8e7e6e5e4e
Revises: f3d914b142ed
Create Date: 2024-07-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e8e7e6e5e4e'
down_revision: Union[str, None] = 'f3d914b142ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tickets', sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()))


def downgrade() -> None:
    op.drop_column('tickets', 'updated_at')
