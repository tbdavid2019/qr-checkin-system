"""
多租戶設置腳本
用於創建示例商戶、員工和API Keys
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import get_db
from services.merchant_service import MerchantService
from services.staff_service import StaffService
from services.event_service import EventService
from schemas.merchant import MerchantCreate
from schemas.staff import StaffCreate
from schemas.event import EventCreate
from app.config import settings

def setup_demo_merchants():
    """設置示例商戶數據"""
    db = next(get_db())
    
    print("🏢 開始設置多租戶示例數據...")
    
    # 創建示例商戶
    merchants_data = [
        {
            "name": "台北演唱會公司",
            "description": "專業演唱會籌辦公司",
            "contact_email": "contact@taipei-concerts.com",
            "contact_phone": "02-1234-5678"
        },
        {
            "name": "高雄展覽中心",
            "description": "大型展覽場地租借",
            "contact_email": "info@kaohsiung-expo.com", 
            "contact_phone": "07-8765-4321"
        },
        {
            "name": "台中會議中心",
            "description": "商務會議場地服務",
            "contact_email": "service@taichung-meetings.com",
            "contact_phone": "04-9988-7766"
        }
    ]
    
    created_merchants = []
    
    for merchant_data in merchants_data:
        try:
            # 檢查商戶是否已存在
            existing_merchants = MerchantService.get_merchants(db)
            if any(m.name == merchant_data["name"] for m in existing_merchants):
                print(f"⚠️  商戶 '{merchant_data['name']}' 已存在，跳過創建")
                merchant = next(m for m in existing_merchants if m.name == merchant_data["name"])
                created_merchants.append(merchant)
                continue
            
            merchant = MerchantService.create_merchant(
                db, 
                MerchantCreate(**merchant_data)
            )
            created_merchants.append(merchant)
            print(f"✅ 創建商戶: {merchant.name} (ID: {merchant.id})")
            
            # 為每個商戶創建API Key
            api_key = MerchantService.create_api_key(
                db=db,
                merchant_id=merchant.id,
                key_name="主要API Key",
                permissions={
                    "events": ["read", "write"],
                    "tickets": ["read", "write"],
                    "staff": ["read", "write"]
                }
            )
            print(f"🔑 創建API Key: {api_key.api_key}")
            
        except Exception as e:
            print(f"❌ 創建商戶失敗: {merchant_data['name']} - {e}")
    
    # 為每個商戶創建員工
    for merchant in created_merchants:
        staff_data = [
            {
                "username": f"staff_{merchant.id}_1",
                "password": "password123",
                "name": f"{merchant.name} - 員工1",
                "email": f"staff1@{merchant.name.lower().replace(' ', '')}.com",
                "role": "admin"
            },
            {
                "username": f"staff_{merchant.id}_2", 
                "password": "password123",
                "name": f"{merchant.name} - 員工2",
                "email": f"staff2@{merchant.name.lower().replace(' ', '')}.com",
                "role": "staff"
            }
        ]
        
        for staff_info in staff_data:
            try:
                # 檢查員工是否已存在
                existing_staff = StaffService.get_staff_by_username(db, staff_info["username"])
                if existing_staff:
                    print(f"⚠️  員工 '{staff_info['username']}' 已存在，跳過創建")
                    continue
                
                staff = StaffService.create_staff(
                    db,
                    StaffCreate(**staff_info),
                    merchant_id=merchant.id
                )
                print(f"👤 為商戶 {merchant.name} 創建員工: {staff.full_name} (用戶名: {staff.username})")
                
            except Exception as e:
                print(f"❌ 創建員工失敗: {staff_info['username']} - {e}")
    
    # 為每個商戶創建示例活動
    for merchant in created_merchants:
        events_data = [
            {
                "name": f"{merchant.name} - 年度音樂節",  # 改為 name
                "description": "大型戶外音樂節活動",
                "start_time": "2024-06-15T18:00:00",
                "end_time": "2024-06-15T23:00:00",
                "location": f"{merchant.name}主場地"
            },
            {
                "name": f"{merchant.name} - 商業會議",  # 改為 name
                "description": "企業年度會議",
                "start_time": "2024-07-20T09:00:00", 
                "end_time": "2024-07-20T17:00:00",
                "location": f"{merchant.name}會議室"
            }
        ]
        
        for event_data in events_data:
            try:
                # 檢查活動是否已存在
                existing_events = EventService.get_events_by_merchant(db, merchant.id)
                if any(e.name == event_data["name"] for e in existing_events):
                    print(f"⚠️  活動 '{event_data['name']}' 已存在，跳過創建")
                    continue
                
                event = EventService.create_event(
                    db,
                    EventCreate(**event_data),
                    merchant_id=merchant.id
                )
                print(f"🎪 為商戶 {merchant.name} 創建活動: {event.name} (ID: {event.id})")
                
            except Exception as e:
                print(f"❌ 創建活動失敗: {event_data['name']} - {e}")
    
    print("\n📊 多租戶設置完成！")
    print("\n商戶資訊摘要:")
    print("-" * 80)
    
    # 顯示商戶資訊摘要
    for merchant in created_merchants:
        api_keys = MerchantService.get_merchant_api_keys(db, merchant.id)
        stats = MerchantService.get_merchant_statistics(db, merchant.id)
        
        print(f"\n🏢 商戶: {merchant.name} (ID: {merchant.id})")
        print(f"   描述: {merchant.description or '無'}")
        print(f"   聯絡電子郵件: {merchant.contact_email or '無'}")
        print(f"   📈 統計: {stats['total_events']} 個活動, {stats['total_staff']} 個員工")
        
        if api_keys:
            active_keys = [k for k in api_keys if k.is_active]
            for key in active_keys:
                print(f"   🔑 API Key: {key.api_key}")
    
    print(f"\n🌐 Gradio 管理介面:")
    print(f"   啟動命令: python gradio_admin.py")
    print(f"   訪問地址: http://localhost:{settings.GRADIO_PORT}")
    print(f"   管理員密碼: {settings.ADMIN_PASSWORD}")
    
    db.close()

def main():
    """主函數"""
    if not settings.ENABLE_MULTI_TENANT:
        print("❌ 多租戶模式未啟用！")
        print("請在 .env 文件中設置 ENABLE_MULTI_TENANT=1")
        return
    
    print("🚀 多租戶模式已啟用")
    setup_demo_merchants()

if __name__ == "__main__":
    main()
