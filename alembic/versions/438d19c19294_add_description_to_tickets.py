"""add description field to tickets table

Revision ID: 438d19c19294
Revises: 797a3c3b3392
Create Date: 2025-06-19 22:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '438d19c19294'
down_revision: Union[str, None] = '797a3c3b3392'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add description field to tickets table."""
    # Check if column already exists before adding
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'tickets' AND column_name = 'description'
    """))
    
    if not result.fetchone():
        # Add description column if it doesn't exist
        op.add_column('tickets', sa.Column('description', sa.Text(), nullable=True, 
                                          comment='JSON format additional information (seat, zone, etc.)'))


def downgrade() -> None:
    """Remove description field from tickets table."""
    # Check if column exists before dropping
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'tickets' AND column_name = 'description'
    """))
    
    if result.fetchone():
        # Drop description column if it exists
        op.drop_column('tickets', 'description')
