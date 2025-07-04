"""Initial schema with Snowflake UUID

Revision ID: 001_init_schema_with_snowflake_uuid
Revises: 
Create Date: 2025-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_init_snowflake'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """創建完整的 schema，包含 Snowflake UUID"""
    
    # 創建 merchants 表格
    op.create_table('merchants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_merchants_id'), 'merchants', ['id'], unique=False)
    
    # 創建 api_keys 表格
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('merchant_id', sa.Integer(), nullable=False),
        sa.Column('key_name', sa.String(length=255), nullable=False),
        sa.Column('api_key', sa.String(length=255), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_key')
    )
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_api_keys_merchant_id'), 'api_keys', ['merchant_id'], unique=False)
    op.create_index(op.f('ix_api_keys_api_key'), 'api_keys', ['api_key'], unique=False)
    
    # 創建 events 表格
    op.create_table('events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('merchant_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('total_quota', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_merchant_id'), 'events', ['merchant_id'], unique=False)
    
    # 創建 ticket_types 表格
    op.create_table('ticket_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('quota', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ticket_types_id'), 'ticket_types', ['id'], unique=False)
    
    # 創建 tickets 表格 (使用 Snowflake ID 作為 uuid)
    op.create_table('tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.BigInteger(), nullable=False),  # Snowflake ID
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('ticket_type_id', sa.Integer(), nullable=True),
        sa.Column('ticket_code', sa.String(length=50), nullable=False),
        sa.Column('holder_name', sa.String(length=100), nullable=False),
        sa.Column('holder_email', sa.String(length=100), nullable=True),
        sa.Column('holder_phone', sa.String(length=20), nullable=True),
        sa.Column('external_user_id', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickets_id'), 'tickets', ['id'], unique=False)
    op.create_index(op.f('ix_tickets_ticket_code'), 'tickets', ['ticket_code'], unique=True)
    op.create_index('ix_tickets_uuid', 'tickets', ['uuid'], unique=True)
    op.create_index(op.f('ix_tickets_external_user_id'), 'tickets', ['external_user_id'], unique=False)
    
    # 創建 staff 表格
    op.create_table('staff',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('merchant_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('login_code', sa.String(length=20), nullable=True),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('login_code')
    )
    op.create_index(op.f('ix_staff_id'), 'staff', ['id'], unique=False)
    op.create_index(op.f('ix_staff_merchant_id'), 'staff', ['merchant_id'], unique=False)
    op.create_index(op.f('ix_staff_username'), 'staff', ['username'], unique=False)
    op.create_index(op.f('ix_staff_email'), 'staff', ['email'], unique=False)
    op.create_index(op.f('ix_staff_login_code'), 'staff', ['login_code'], unique=False)
    
    # 創建 staff_events 表格 (多對多關係)
    op.create_table('staff_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('can_checkin', sa.Boolean(), nullable=True, default=True),
        sa.Column('can_revoke', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建 checkin_logs 表格
    op.create_table('checkin_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=True),
        sa.Column('checkin_time', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=True, default=False),
        sa.Column('revoked_by', sa.Integer(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
        sa.ForeignKeyConstraint(['revoked_by'], ['staff.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkin_logs_id'), 'checkin_logs', ['id'], unique=False)


def downgrade() -> None:
    """刪除所有表格"""
    op.drop_table('checkin_logs')
    op.drop_table('staff_events')
    op.drop_table('staff')
    op.drop_table('tickets')
    op.drop_table('ticket_types')
    op.drop_table('events')
    op.drop_table('api_keys')
    op.drop_table('merchants')
