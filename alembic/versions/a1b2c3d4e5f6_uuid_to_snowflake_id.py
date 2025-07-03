"""UUID to Snowflake ID migration

Revision ID: a1b2c3d4e5f6
Revises: 5b035bda1530
Create Date: 2025-01-03 16:44:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5b035bda1530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """升級：UUID → Snowflake ID"""
    
    # 1. 備份現有資料（測試環境可選）
    op.execute("CREATE TABLE IF NOT EXISTS tickets_uuid_backup AS SELECT id, uuid FROM tickets;")
    
    # 2. 移除 UUID 相關約束和索引
    op.drop_index('ix_tickets_uuid', table_name='tickets')
    
    # 3. 清空 uuid 欄位，準備型別轉換
    # 測試環境：直接用 id 作為臨時值
    op.execute("UPDATE tickets SET uuid = CAST(id AS TEXT)::UUID WHERE uuid IS NOT NULL;")
    
    # 4. 修改欄位型別：UUID → BIGINT
    op.alter_column('tickets', 'uuid',
                    existing_type=postgresql.UUID(as_uuid=True),
                    type_=sa.BigInteger(),
                    existing_nullable=False,
                    postgresql_using='CAST(CAST(uuid AS TEXT) AS BIGINT)')
    
    # 5. 更新所有現有票券的 uuid 為 Snowflake ID
    # 注意：這會讓所有現有 QR Code 失效
    op.execute("""
        UPDATE tickets 
        SET uuid = CAST(EXTRACT(EPOCH FROM created_at) * 1000 AS BIGINT) << 22 | id
        WHERE uuid IS NOT NULL;
    """)
    
    # 6. 重建索引
    op.create_index('ix_tickets_uuid', 'tickets', ['uuid'], unique=True)
    
    # 7. 移除預設值（改由應用程式生成）
    op.alter_column('tickets', 'uuid', server_default=None)

def downgrade() -> None:
    """降級：Snowflake ID → UUID"""
    
    # 警告：這是破壞性操作
    op.execute("TRUNCATE TABLE tickets CASCADE;")
    
    # 恢復 UUID 型別
    op.drop_index('ix_tickets_uuid', table_name='tickets')
    
    op.alter_column('tickets', 'uuid',
                    existing_type=sa.BigInteger(),
                    type_=postgresql.UUID(as_uuid=True),
                    existing_nullable=False,
                    server_default=sa.text('gen_random_uuid()'))
    
    op.create_index('ix_tickets_uuid', 'tickets', ['uuid'], unique=True)