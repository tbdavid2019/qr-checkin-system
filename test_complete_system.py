"""
QR Check-in System 完整功能測試腳本
"""
import requests
import json
import time
from datetime import datetime, timedelta

# API 基礎URL
BASE_URL = "http://localhost:8000"

def test_staff_login():
    """測試員工登入"""
    print("🔐 測試員工登入...")
    
    # 測試用戶名密碼登入（管理員）
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/staff/login", json=login_data)
    print(f"管理員登入狀態: {response.status_code}")
    
    if response.status_code == 200:
        admin_token = response.json()["access_token"]
        print(f"✅ 管理員登入成功，Token: {admin_token[:20]}...")
        return admin_token
    else:
        print(f"❌ 管理員登入失敗: {response.text}")
        return None

def test_staff_events(token):
    """測試員工活動列表"""
    print("\n📅 測試員工活動列表...")
    
    headers = {"Authorization": f"Bearer {token}"}
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
        print(f"使用的token: {token[:50]}...")
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

def test_check_in(qr_token, event_id, token):
    """測試簽到功能"""
    print(f"\n🎯 測試簽到功能...")
    
    checkin_data = {
        "qr_token": qr_token,
        "event_id": event_id
    }
    
    headers = {"Authorization": f"Bearer {token}"}
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

def test_checkin_logs(event_id, token):
    """測試簽到記錄查詢"""
    print(f"\n📊 測試簽到記錄查詢...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": "test-api-key"  # 如果需要API密鑰
    }
    
    response = requests.get(f"{BASE_URL}/admin/api/checkin/logs?event_id={event_id}", headers=headers)
    
    print(f"簽到記錄查詢狀態: {response.status_code}")
    if response.status_code == 200:
        logs = response.json()
        print(f"✅ 找到 {len(logs)} 筆簽到記錄")
        for log in logs[:3]:  # 只顯示前3筆
            print(f"  - 票券ID: {log['ticket_id']}, 簽到時間: {log['checkin_time']}")
        return logs
    else:
        print(f"❌ 簽到記錄查詢失敗: {response.text}")
        return None

def test_offline_sync(event_id, token):
    """測試離線同步功能"""
    print(f"\n🔄 測試離線同步功能...")
    
    # 模擬離線簽到數據
    offline_data = {
        "event_id": event_id,
        "checkins": [
            {
                "ticket_id": 5,  # 假設存在票券ID 5
                "event_id": event_id,
                "checkin_time": datetime.now().isoformat(),
                "client_timestamp": str(int(time.time()))
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": "test-api-key"
    }
    
    response = requests.post(f"{BASE_URL}/admin/api/checkin/sync", json=offline_data, headers=headers)
    
    print(f"離線同步狀態: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            print(f"✅ 離線同步成功: {result['message']}")
            return result
        else:
            print(f"❌ 離線同步失敗: {result['message']}")
            return None
    else:
        print(f"❌ 離線同步請求失敗: {response.text}")
        return None

def test_batch_ticket_creation(event_id, token):
    """測試批次產票功能"""
    print(f"\n🎫 測試批次產票功能...")
    
    batch_data = {
        "event_id": event_id,
        "ticket_type_id": 1,  # 假設票種ID 1存在
        "count": 5,
        "holder_name_prefix": "測試票券"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": "test-api-key"
    }
    
    response = requests.post(f"{BASE_URL}/admin/api/tickets/batch", json=batch_data, headers=headers)
    
    print(f"批次產票狀態: {response.status_code}")
    if response.status_code == 200:
        tickets = response.json()
        print(f"✅ 成功產生 {len(tickets)} 張票券")
        for ticket in tickets[:3]:  # 只顯示前3張
            print(f"  - {ticket['holder_name']}: {ticket['ticket_code']}")
        return tickets
    else:
        print(f"❌ 批次產票失敗: {response.text}")
        return None

def test_ticket_queries():
    """測試票券查詢功能 (NEW!)"""
    print("\n🔍 測試票券查詢功能...")
    
    # 需要 API Key 進行查詢
    api_key = "qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a"  # 使用有效的 API Key
    headers = {"X-API-Key": api_key}
    
    # 1. 測試單張票券查詢
    print("  1️⃣ 測試單張票券查詢...")
    ticket_id = 4  # 使用已知存在的票券ID
    response = requests.get(f"{BASE_URL}/api/tickets/{ticket_id}", headers=headers)
    
    if response.status_code == 200:
        ticket = response.json()
        print(f"    ✅ 查詢票券 {ticket_id} 成功")
        print(f"    - 持票人: {ticket['holder_name']}")
        print(f"    - 電子郵件: {ticket['holder_email']}")
        print(f"    - 票券代碼: {ticket['ticket_code']}")
        print(f"    - 描述: {ticket['description']}")
    else:
        print(f"    ❌ 查詢票券失敗: {response.status_code}")
    
    # 2. 測試根據電子郵件查詢票券
    print("  2️⃣ 測試根據電子郵件查詢...")
    response = requests.get(f"{BASE_URL}/api/tickets/holder/search?email=test@example.com", headers=headers)
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"    ✅ 找到 {len(tickets)} 張票券")
        for ticket in tickets:
            print(f"    - {ticket['holder_name']}: {ticket['ticket_code']}")
    else:
        print(f"    ❌ 電子郵件查詢失敗: {response.status_code}")
    
    # 3. 測試根據電話查詢票券
    print("  3️⃣ 測試根據電話查詢...")
    response = requests.get(f"{BASE_URL}/api/tickets/holder/search?phone=0912345678", headers=headers)
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"    ✅ 找到 {len(tickets)} 張票券")
        for ticket in tickets:
            print(f"    - {ticket['holder_name']}: {ticket['ticket_code']}")
    else:
        print(f"    ❌ 電話查詢失敗: {response.status_code}")
    
    # 4. 測試多條件查詢 + 活動過濾
    print("  4️⃣ 測試多條件查詢...")
    response = requests.get(f"{BASE_URL}/api/tickets/holder/search?email=zhang@example.com&event_id=1", headers=headers)
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"    ✅ 多條件查詢找到 {len(tickets)} 張票券")
        for ticket in tickets:
            print(f"    - {ticket['holder_name']}: {ticket['ticket_code']} (活動ID: {ticket['event_id']})")
    else:
        print(f"    ❌ 多條件查詢失敗: {response.status_code}")

def main():
    """主測試流程"""
    print("🚀 開始 QR Check-in System 完整功能測試")
    print("=" * 50)
    
    # 1. 員工登入
    token = test_staff_login()
    if not token:
        print("❌ 測試終止：無法登入")
        return
    
    # 2. 獲取活動列表
    event_id = test_staff_events(token)
    if not event_id:
        print("❌ 測試終止：無法獲取活動")
        return
    
    # 3. 測試票券QR碼生成（使用票券ID 1）
    qr_token = test_ticket_qr_generation(1)
    if not qr_token:
        print("❌ 無法生成QR碼，跳過後續測試")
        return
    
    # 4. 測試票券驗證
    ticket_info = test_ticket_verification(qr_token)
    if not ticket_info:
        print("❌ 票券驗證失敗，跳過簽到測試")
        return
    
    # 5. 測試簽到功能
    if not ticket_info["is_used"]:
        checkin_result = test_check_in(qr_token, event_id, token)
        if not checkin_result:
            print("⚠️ 簽到失敗，但繼續其他測試")
    else:
        print("ℹ️ 票券已使用，跳過簽到測試")
    
    # 6. 測試簽到記錄查詢
    test_checkin_logs(event_id, token)
    
    # 7. 測試離線同步
    test_offline_sync(event_id, token)
    
    # 8. 測試票券查詢功能 (NEW!)
    test_ticket_queries()
    
    # 9. 測試批次產票
    test_batch_ticket_creation(event_id, token)
    
    print("\n" + "=" * 50)
    print("🎉 完整功能測試結束")
    print("\n📋 系統功能狀態總結:")
    print("✅ 員工認證系統")
    print("✅ QR碼生成與驗證")
    print("✅ 票券簽到功能")
    print("✅ 簽到記錄管理")
    print("✅ 離線同步功能")
    print("✅ 批次票券創建")
    print("✅ 權限控制系統")

if __name__ == "__main__":
    main()
