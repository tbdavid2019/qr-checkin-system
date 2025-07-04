#!/usr/bin/env python3
"""
測試建立票券和 Snowflake ID
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app.database import get_db
from services.ticket_service import TicketService
from schemas.ticket import TicketCreate
from models.event import Event

def test_create_ticket():
    """測試建立票券"""
    db = next(get_db())
    
    try:
        # 1. 獲取第一個活動
        event = db.query(Event).first()
        if not event:
            print("❌ 沒有找到活動")
            return
            
        print(f"📅 使用活動: {event.name} (ID: {event.id})")
        
        # 2. 建立測試票券
        ticket_data = TicketCreate(
            event_id=event.id,
            holder_name="測試用戶",
            holder_email="test@example.com",
            holder_phone="0912345678"
        )
        
        print("🎫 正在建立票券...")
        ticket = TicketService.create_ticket(db, ticket_data)
        
        print(f"✅ 票券建立成功！")
        print(f"   - ID: {ticket.id}")
        print(f"   - UUID (Snowflake): {ticket.uuid}")
        print(f"   - 票券代碼: {ticket.ticket_code}")
        print(f"   - 持有人: {ticket.holder_name}")
        print(f"   - UUID 類型: {type(ticket.uuid)}")
        
        # 3. 檢查 UUID 是否為 Snowflake ID 格式 (應該是大整數)
        if isinstance(ticket.uuid, int) and ticket.uuid > 0:
            print(f"✅ Snowflake ID 格式正確: {ticket.uuid}")
        else:
            print(f"❌ UUID 格式錯誤: {ticket.uuid} (類型: {type(ticket.uuid)})")
            
    except Exception as e:
        print(f"❌ 建立票券失敗: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_create_ticket()
