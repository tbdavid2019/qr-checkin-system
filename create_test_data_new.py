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

def create_test_data():
    """創建多租戶測試數據"""
    db = next(get_db())
    
    try:
        print("🏢 開始創建測試數據...")
        
        # 1. 創建測試商戶
        merchant_data = MerchantCreate(
            name="測試演唱會公司",
            description="用於測試的演唱會公司",
            contact_email="test@concerts.com",
            contact_phone="02-1234-5678"
        )
        
        merchant = MerchantService.create_merchant(db, merchant_data)
        print(f"✅ 建立商戶: {merchant.name} (ID: {merchant.id})")
        
        # 獲取商戶的 API key
        api_key = merchant.api_keys[0].api_key if merchant.api_keys else None
        print(f"📑 商戶 API Key: {api_key}")
        
        # 2. 創建測試活動
        event_data = EventCreate(
            name="2024 科技研討會",
            description="年度科技趨勢研討會",
            start_time=datetime.now() + timedelta(days=7),
            end_time=datetime.now() + timedelta(days=7, hours=8),
            location="台北國際會議中心",
            total_quota=200
        )
        
        event = EventService.create_event(db, event_data, merchant.id)
        print(f"✅ 建立活動: {event.name} (ID: {event.id})")
        
        # 3. 創建票種
        ticket_types_data = [
            TicketTypeCreate(
                name="一般票",
                price=1500.00,
                quota=100
            ),
            TicketTypeCreate(
                name="VIP票", 
                price=3000.00,
                quota=20
            ),
            TicketTypeCreate(
                name="學生票",
                price=800.00,
                quota=50
            )
        ]
        
        created_ticket_types = []
        for ticket_type_data in ticket_types_data:
            ticket_type = EventService.create_ticket_type(db, event.id, ticket_type_data)
            created_ticket_types.append(ticket_type)
            print(f"✅ 建立票種: {ticket_type.name} (ID: {ticket_type.id})")
        
        # 4. 創建測試員工
        staff_data = [
            StaffCreate(
                username="admin",
                email="admin@example.com",
                password="admin123",
                full_name="系統管理員"
            ),
            StaffCreate(
                username="scanner1",
                email="scanner1@example.com", 
                password="password123",
                full_name="掃描員一號"
            ),
            StaffCreate(
                username="scanner2",
                email="scanner2@example.com",
                password="password123", 
                full_name="掃描員二號"
            )
        ]
        
        created_staff = []
        for staff_info in staff_data:
            staff = StaffService.create_staff(db, staff_info, merchant.id)
            created_staff.append(staff)
            print(f"✅ 建立員工: {staff.full_name} (用戶名: {staff.username})")
        
        # 5. 指派員工到活動 (給予簽到權限)
        for staff in created_staff:
            StaffService.assign_staff_to_event(db, staff.id, event.id, can_checkin=True, can_revoke=True)
            print(f"✅ 指派員工 {staff.full_name} 到活動 {event.name}")
        
        # 6. 創建測試票券
        test_tickets_data = [
            {
                "holder_name": "測試用戶",
                "holder_email": "test@example.com",
                "ticket_type_id": created_ticket_types[0].id,  # 一般票
                "description": '{"seat": "A-01", "zone": "一般區", "entrance": "正門"}'
            },
            {
                "holder_name": "張三",
                "holder_email": "zhang@example.com", 
                "ticket_type_id": created_ticket_types[1].id,  # VIP票
                "description": '{"seat": "V-05", "zone": "VIP區", "entrance": "VIP專用門"}'
            },
            {
                "holder_name": "李四",
                "holder_email": "li@example.com",
                "ticket_type_id": created_ticket_types[2].id,  # 學生票
                "description": '{"seat": "S-25", "zone": "學生區", "entrance": "側門", "student_id": "B10512345"}'
            }
        ]
        
        for ticket_data in test_tickets_data:
            ticket_create = TicketCreate(
                holder_name=ticket_data["holder_name"],
                holder_email=ticket_data["holder_email"],
                ticket_type_id=ticket_data["ticket_type_id"],
                description=ticket_data["description"]
            )
            ticket = TicketService.create_ticket(db, ticket_create, event.id)
            print(f"✅ 建立票券: {ticket.holder_name} - {ticket.ticket_code}")
        
        print("\n🎉 測試數據建立完成！")
        print(f"\n📋 登入資訊:")
        print(f"商戶 API Key: {api_key}")
        print("員工帳號:")
        for staff_info in staff_data:
            print(f"  - 用戶名: {staff_info.username}, 密碼: {staff_info.password}")
        
        return True
        
    except Exception as e:
        print(f"❌ 建立測試數據失敗: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_test_data()
    if success:
        print("\n✅ 測試數據創建成功！可以開始使用系統進行測試。")
    else:
        print("\n❌ 測試數據創建失敗！請檢查錯誤訊息。")
