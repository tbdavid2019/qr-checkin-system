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
            
            # 先創建商戶並獲取返回的字典
            merchant_data_obj = MerchantCreate(**merchant_data)
            merchant_dict = MerchantService.create_merchant(db, merchant_data_obj)
            
            # 通過 ID 查詢商戶實體物件
            merchant_id = merchant_dict["id"]
            merchant = MerchantService.get_merchant_by_id(db, merchant_id)
            
            if merchant:
                created_merchants.append(merchant)
                print(f"✅ 創建商戶: {merchant.name} (ID: {merchant.id})")
                print(f"🔑 預設API Key: {merchant_dict['api_key']}")
            else:
                print(f"⚠️ 無法獲取商戶物件，ID: {merchant_id}")
            
        except Exception as e:
            print(f"❌ 創建商戶失敗: {merchant_data['name']} - {e}")
    
    # 為每個商戶創建員工
    for merchant in created_merchants:
        try:
            # 創建第一個員工 (管理員)
            username1 = f"staff_{merchant.id}_1"
            existing_staff1 = StaffService.get_staff_by_username(db, username1)
            if existing_staff1:
                print(f"⚠️  員工 '{username1}' 已存在，跳過創建")
            else:
                staff_create_1 = StaffCreate(
                    username=username1,
                    password="password123",
                    full_name=f"{merchant.name} - 員工1",
                    email=f"staff1@{merchant.name.lower().replace(' ', '')}.com",
                    role="admin"
                )
                
                staff1 = StaffService.create_staff(
                    db,
                    staff_create_1,
                    merchant_id=merchant.id
                )
                print(f"👤 為商戶 {merchant.name} 創建員工: {staff1.full_name} (用戶名: {staff1.username})")
            
            # 創建第二個員工 (一般人員)
            username2 = f"staff_{merchant.id}_2"
            existing_staff2 = StaffService.get_staff_by_username(db, username2)
            if existing_staff2:
                print(f"⚠️  員工 '{username2}' 已存在，跳過創建")
            else:
                staff_create_2 = StaffCreate(
                    username=username2,
                    password="password123",
                    full_name=f"{merchant.name} - 員工2",
                    email=f"staff2@{merchant.name.lower().replace(' ', '')}.com",
                    role="staff"
                )
                
                staff2 = StaffService.create_staff(
                    db,
                    staff_create_2,
                    merchant_id=merchant.id
                )
                print(f"👤 為商戶 {merchant.name} 創建員工: {staff2.full_name} (用戶名: {staff2.username})")
                
        except Exception as e:
            print(f"❌ 創建員工失敗: {e}")
            import traceback
            print(f"詳細錯誤: {traceback.format_exc()}")
    
    # 為每個商戶創建示例活動
    for merchant in created_merchants:
        events_data = [
            {
                "name": f"{merchant.name} - 年度音樂節",
                "description": "大型戶外音樂節活動",
                "start_time": "2024-06-15T18:00:00",
                "end_time": "2024-06-15T23:00:00",
                "location": f"{merchant.name}主場地",
                "total_quota": 5000
            },
            {
                "name": f"{merchant.name} - 商業會議",
                "description": "企業年度會議",
                "start_time": "2024-07-20T09:00:00", 
                "end_time": "2024-07-20T17:00:00",
                "location": f"{merchant.name}會議室",
                "total_quota": 200
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
