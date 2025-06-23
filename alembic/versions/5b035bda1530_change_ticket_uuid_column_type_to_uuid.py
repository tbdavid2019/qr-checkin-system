"""Change ticket uuid column type to UUID

Revision ID: 5b035bda1530
Revises: ef10c83cabbf
Create Date: 2025-06-23 01:40:38.891904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5b035bda1530'
down_revision: Union[str, None] = 'ef10c83cabbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('tickets', 'uuid',
               existing_type=sa.VARCHAR(length=36),
               type_=postgresql.UUID(as_uuid=True),
               existing_nullable=False,
               existing_server_default=sa.text('gen_random_uuid()'),
               postgresql_using='uuid::uuid')
    op.drop_constraint('uq_tickets_uuid', 'tickets', type_='unique')
    op.create_index(op.f('ix_tickets_uuid'), 'tickets', ['uuid'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tickets_uuid'), table_name='tickets')
    op.create_unique_constraint('uq_tickets_uuid', 'tickets', ['uuid'])
    op.alter_column('tickets', 'uuid',
               existing_type=postgresql.UUID(as_uuid=True),
               type_=sa.VARCHAR(length=36),
               existing_nullable=False,
               existing_server_default=sa.text('gen_random_uuid()'))
