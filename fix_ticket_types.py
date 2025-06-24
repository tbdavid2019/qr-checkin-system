#!/usr/bin/env python3
"""
修復現有票券的票種問題
為沒有票種的票券建立並指定預設票種
"""

import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Event, TicketType, Ticket

# 從環境變數獲取資料庫連接
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://qr_admin:qr_pass@db:5432/qr_system")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_tickets_without_ticket_type():
    """修復沒有票種的票券"""
    db = SessionLocal()
    try:
        print("🔍 開始修復沒有票種的票券...")
        
        # 查找所有沒有票種的票券
        tickets_without_type = db.query(Ticket).filter(Ticket.ticket_type_id.is_(None)).all()
        print(f"📊 找到 {len(tickets_without_type)} 張沒有票種的票券")
        
        if not tickets_without_type:
            print("✅ 沒有需要修復的票券")
            return
        
        # 按活動分組處理
        events_to_fix = {}
        for ticket in tickets_without_type:
            if ticket.event_id not in events_to_fix:
                events_to_fix[ticket.event_id] = []
            events_to_fix[ticket.event_id].append(ticket)
        
        print(f"📋 需要處理 {len(events_to_fix)} 個活動")
        
        for event_id, tickets in events_to_fix.items():
            print(f"\n🎯 處理活動 ID: {event_id}")
            
            # 獲取活動資訊
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                print(f"❌ 活動 {event_id} 不存在，跳過")
                continue
            
            print(f"   活動名稱: {event.name}")
            print(f"   需要修復的票券數量: {len(tickets)}")
            
            # 查找或建立預設票種
            default_ticket_type = db.query(TicketType).filter(
                TicketType.event_id == event_id,
                TicketType.name == "一般票"
            ).first()
            
            if not default_ticket_type:
                # 建立預設票種
                # 計算建議的配額：現有票券數量（包括沒票種的）
                total_tickets_count = db.query(Ticket).filter(Ticket.event_id == event_id).count()
                suggested_quota = max(total_tickets_count, event.total_quota or 0)
                
                default_ticket_type = TicketType(
                    event_id=event_id,
                    name="一般票",
                    quota=suggested_quota,
                    is_active=True
                )
                db.add(default_ticket_type)
                db.commit()
                db.refresh(default_ticket_type)
                print(f"   ✅ 建立預設票種: {default_ticket_type.name} (配額: {suggested_quota})")
            else:
                print(f"   📋 使用現有票種: {default_ticket_type.name} (配額: {default_ticket_type.quota})")
            
            # 更新所有沒有票種的票券
            for ticket in tickets:
                ticket.ticket_type_id = default_ticket_type.id
                print(f"   🎫 更新票券 {ticket.ticket_code} -> {default_ticket_type.name}")
            
            db.commit()
            print(f"   ✅ 活動 {event_id} 修復完成")
        
        print(f"\n🎉 修復完成！總共處理了 {len(tickets_without_type)} 張票券")
        
    except Exception as e:
        print(f"❌ 修復過程中發生錯誤: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_tickets_without_ticket_type()
