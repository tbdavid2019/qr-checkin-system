"""
添加測試數據 (Multi-tenant Version)
使用新的多租戶架構創建測試數據
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from services.merchant_service import MerchantService
from services.staff_service import StaffService
from services.event_service import EventService
from services.ticket_service import TicketService
from schemas.merchant import MerchantCreate
from schemas.staff import StaffCreate
from schemas.event import EventCreate
from schemas.ticket import TicketTypeCreate, TicketCreate
from utils.security import get_password_hash

def create_test_data():
    db: Session = SessionLocal()
    
    try:
        # 1. 建立測試活動
        event = Event(
            name="2024 科技研討會",
            description="年度科技趨勢研討會",
            start_time=datetime.now() + timedelta(days=7),
            end_time=datetime.now() + timedelta(days=7, hours=8),
            location="台北國際會議中心",
            is_active=True
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        print(f"✅ 建立活動: {event.name} (ID: {event.id})")
        
        # 2. 建立票種
        ticket_types = [
            TicketType(
                event_id=event.id,
                name="一般票",
                price=1500.00,
                quota=100,
                is_active=True
            ),
            TicketType(
                event_id=event.id,
                name="VIP票",
                price=3000.00,
                quota=20,
                is_active=True
            ),
            TicketType(
                event_id=event.id,
                name="學生票",
                price=800.00,
                quota=50,
                is_active=True
            )
        ]
        
        for ticket_type in ticket_types:
            db.add(ticket_type)
        db.commit()
        
        for ticket_type in ticket_types:
            db.refresh(ticket_type)
            print(f"✅ 建立票種: {ticket_type.name} (ID: {ticket_type.id})")
        
        # 3. 建立測試員工
        staff_members = [
            Staff(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                login_code=generate_login_code(),
                full_name="系統管理員",
                is_active=True,
                is_admin=True
            ),
            Staff(
                username="scanner1",
                email="scanner1@example.com",
                login_code=generate_login_code(),
                full_name="掃描員一號",
                is_active=True,
                is_admin=False
            ),
            Staff(
                username="scanner2",
                email="scanner2@example.com",
                login_code=generate_login_code(),
                full_name="掃描員二號",
                is_active=True,
                is_admin=False
            )
        ]
        
        for staff in staff_members:
            db.add(staff)
        db.commit()
        
        for staff in staff_members:
            db.refresh(staff)
            print(f"✅ 建立員工: {staff.full_name} (用戶名: {staff.username}, 登入碼: {staff.login_code})")
        
        # 4. 設定員工活動權限
        for staff in staff_members:
            staff_event = StaffEvent(
                staff_id=staff.id,
                event_id=event.id,
                can_checkin=True,
                can_revoke=staff.is_admin  # 只有管理員可以撤銷
            )
            db.add(staff_event)
        
        db.commit()
        print(f"✅ 設定員工活動權限")
        
        # 5. 建立測試票券
        test_tickets = [
            Ticket(
                event_id=event.id,
                ticket_type_id=ticket_types[0].id,  # 一般票
                ticket_code=generate_ticket_code(),
                holder_name="張三",
                holder_email="zhang@example.com",
                holder_phone="0912345678",
                description='{"seat": "A-01", "zone": "一般區", "entrance": "正門", "meal": "葷食"}'
            ),
            Ticket(
                event_id=event.id,
                ticket_type_id=ticket_types[1].id,  # VIP票
                ticket_code=generate_ticket_code(),
                holder_name="李四",
                holder_email="li@example.com",
                holder_phone="0987654321",
                description='{"seat": "VIP-05", "zone": "VIP區", "entrance": "VIP專屬入口", "meal": "素食", "parking": "B1-VIP車位"}'
            ),
            Ticket(
                event_id=event.id,
                ticket_type_id=ticket_types[2].id,  # 學生票
                ticket_code=generate_ticket_code(),
                holder_name="王五",
                holder_email="wang@example.com",
                is_used=False,
                description='{"seat": "S-25", "zone": "學生區", "entrance": "側門", "student_id": "B10512345"}'
            )
        ]
        
        for ticket in test_tickets:
            db.add(ticket)
        db.commit()
        
        for ticket in test_tickets:
            db.refresh(ticket)
            print(f"✅ 建立票券: {ticket.holder_name} - {ticket.ticket_code} (座位: {ticket.description})")
        
        print("\n🎉 測試數據建立完成！")
        print("\n📋 登入資訊:")
        print("管理員 - 用戶名: admin, 密碼: admin123")
        for staff in staff_members:
            if not staff.is_admin:
                print(f"{staff.full_name} - 登入碼: {staff.login_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 建立測試數據失敗: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
