"""add uuid to tickets table

Revision ID: ef10c83cabbf
Revises: 438d19c19294
Create Date: 2025-06-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = 'ef10c83cabbf'
down_revision: Union[str, None] = '438d19c19294'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tickets', sa.Column('uuid', sa.String(36), nullable=False, server_default=sa.text('gen_random_uuid()')))
    op.create_unique_constraint('uq_tickets_uuid', 'tickets', ['uuid'])


def downgrade() -> None:
    op.drop_constraint('uq_tickets_uuid', 'tickets', type_='unique')
    op.drop_column('tickets', 'uuid')
