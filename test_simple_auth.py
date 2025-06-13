"""
簡化版 QR Check-in System 測試腳本
使用 API Key + Staff ID 認證
"""
import requests
import json

# API 基礎URL
BASE_URL = "http://localhost:8000"

# 認證設定
API_KEY = "test-api-key"  # 在config.py中設定的API_KEY
STAFF_ID = 1  # 管理員ID

def test_staff_verification():
    """測試員工身份驗證"""
    print("🔐 測試員工身份驗證...")
    
    # 測試用戶名密碼驗證
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/staff/verify", json=login_data)
    print(f"員工驗證狀態: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 員工驗證成功")
        print(f"  - 員工ID: {result['staff_id']}")
        print(f"  - 姓名: {result['full_name']}")
        return result['staff_id']
    else:
        print(f"❌ 員工驗證失敗: {response.text}")
        return None

def test_staff_profile():
    """測試員工資料獲取"""
    print("\n👤 測試員工資料獲取...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Staff-ID": str(STAFF_ID)
    }
    
    response = requests.get(f"{BASE_URL}/api/staff/profile", headers=headers)
    print(f"員工資料查詢狀態: {response.status_code}")
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ 員工資料獲取成功")
        print(f"  - 用戶名: {profile['username']}")
        print(f"  - 姓名: {profile['full_name']}")
        print(f"  - 是否為管理員: {profile['is_admin']}")
        return profile
    else:
        print(f"❌ 員工資料獲取失敗: {response.text}")
        return None

def test_staff_events():
    """測試員工活動列表"""
    print("\n📅 測試員工活動列表...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Staff-ID": str(STAFF_ID)
    }
    
    response = requests.get(f"{BASE_URL}/api/staff/events", headers=headers)
    print(f"活動列表查詢狀態: {response.status_code}")
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ 找到 {len(events)} 個活動")
        for event in events:
            print(f"  - {event['event_name']} (ID: {event['event_id']})")
        return events[0]['event_id'] if events else None
    else:
        print(f"❌ 活動列表查詢失敗: {response.text}")
        return None

def test_ticket_qr_generation(ticket_id):
    """測試票券QR碼生成"""
    print(f"\n🎫 測試票券 {ticket_id} QR碼生成...")
    
    response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}/qrcode")
    
    print(f"QR碼生成狀態: {response.status_code}")
    if response.status_code == 200:
        qr_data = response.json()
        print(f"✅ QR碼生成成功")
        print(f"  - 票券代碼: {qr_data['ticket_code']}")
        print(f"  - 持票人: {qr_data['holder_name']}")
        print(f"  - QR Token: {qr_data['qr_token'][:20]}...")
        return qr_data['qr_token']
    else:
        print(f"❌ QR碼生成失敗: {response.text}")
        return None

def test_ticket_verification(qr_token):
    """測試票券驗證"""
    print(f"\n✅ 測試票券驗證...")
    
    verify_data = {"qr_token": qr_token}
    response = requests.post(f"{BASE_URL}/api/tickets/verify", json=verify_data)
    
    print(f"票券驗證狀態: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result["valid"]:
            print(f"✅ 票券驗證成功")
            print(f"  - 持票人: {result['holder_name']}")
            print(f"  - 票種: {result['ticket_type_name']}")
            print(f"  - 已使用: {result['is_used']}")
            return result
        else:
            print(f"❌ 票券無效: {result['message']}")
            return None
    else:
        print(f"❌ 票券驗證失敗: {response.text}")
        return None

def test_check_in(qr_token, event_id):
    """測試簽到功能"""
    print(f"\n🎯 測試簽到功能...")
    
    checkin_data = {
        "qr_token": qr_token,
        "event_id": event_id
    }
    
    headers = {
        "X-API-Key": API_KEY,
        "Staff-ID": str(STAFF_ID)
    }
    
    response = requests.post(f"{BASE_URL}/api/checkin", json=checkin_data, headers=headers)
    
    print(f"簽到狀態: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            print(f"✅ 簽到成功")
            print(f"  - 持票人: {result['holder_name']}")
            print(f"  - 簽到時間: {result['checkin_time']}")
            return result
        else:
            print(f"❌ 簽到失敗: {result['message']}")
            return None
    else:
        print(f"❌ 簽到請求失敗: {response.text}")
        return None

def main():
    """主測試流程"""
    print("🚀 開始簡化版 QR Check-in System 測試")
    print("認證方式: API Key + Staff ID")
    print("=" * 50)
    
    # 1. 員工身份驗證
    staff_id = test_staff_verification()
    if not staff_id:
        print("❌ 測試終止：員工驗證失敗")
        return
    
    # 2. 測試員工資料獲取
    profile = test_staff_profile()
    if not profile:
        print("❌ 測試終止：無法獲取員工資料")
        return
    
    # 3. 獲取活動列表
    event_id = test_staff_events()
    if not event_id:
        print("❌ 測試終止：無法獲取活動")
        return
    
    # 4. 測試票券QR碼生成（使用票券ID 1）
    qr_token = test_ticket_qr_generation(1)
    if not qr_token:
        print("❌ 無法生成QR碼，跳過後續測試")
        return
    
    # 5. 測試票券驗證
    ticket_info = test_ticket_verification(qr_token)
    if not ticket_info:
        print("❌ 票券驗證失敗，跳過簽到測試")
        return
    
    # 6. 測試簽到功能
    if not ticket_info["is_used"]:
        checkin_result = test_check_in(qr_token, event_id)
        if not checkin_result:
            print("⚠️ 簽到失敗，但繼續測試")
    else:
        print("ℹ️ 票券已使用，跳過簽到測試")
    
    print("\n" + "=" * 50)
    print("🎉 簡化版系統測試結束")
    print("\n📋 認證方式說明:")
    print("✅ 使用 X-API-Key 和 Staff-ID 標頭進行認證")
    print("✅ 不需要JWT token，更簡單直接")
    print("✅ 適合快速開發和測試環境")

if __name__ == "__main__":
    main()
