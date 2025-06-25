"""
QR Check-in System 完整功能演示腳本 (Multi-tenant Version)
展示多租戶系統的所有主要功能，使用 JWT 認證
"""
import requests
import json
import time

# API 基礎URL
BASE_URL = "http://localhost:8000"

# 全域變數存儲認證資訊
MERCHANT_API_KEY = None
STAFF_JWT_TOKEN = None
CURRENT_MERCHANT_ID = None
CURRENT_STAFF_ID = None

def print_section(title):
    """打印章節標題"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_subsection(title):
    """打印子章節標題"""
    print(f"\n📌 {title}")
    print('-'*40)

def api_request(method, endpoint, data=None, headers=None, use_staff_auth=False, use_merchant_auth=False):
    """統一的API請求函數"""
    url = f"{BASE_URL}{endpoint}"
    default_headers = {"Content-Type": "application/json"}
    
    if use_staff_auth and STAFF_JWT_TOKEN:
        default_headers["Authorization"] = f"Bearer {STAFF_JWT_TOKEN}"
    
    if use_merchant_auth and MERCHANT_API_KEY:
        default_headers["X-API-Key"] = MERCHANT_API_KEY
    
    if headers:
        default_headers.update(headers)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=default_headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=default_headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=default_headers, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=default_headers, timeout=10)
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ API 請求失敗: {e}")
        return None

def setup_authentication():
    """設置認證資訊"""
    global MERCHANT_API_KEY, STAFF_JWT_TOKEN, CURRENT_MERCHANT_ID, CURRENT_STAFF_ID
    
    print_section("認證設置")
    
    # 從已有的商戶中獲取 API key (假設 setup_multi_tenant.py 已經執行)
    print("📋 請提供商戶 API Key (可在 setup_multi_tenant.py 執行後獲得):")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ 需要提供有效的 API Key")
        return False
    
    MERCHANT_API_KEY = api_key
    
    # 員工登入
    print("\n📋 員工登入:")
    username = input("員工用戶名 (預設: staff_1_1): ").strip() or "staff_1_1"
    password = input("員工密碼 (預設: password123): ").strip() or "password123"
    
    login_data = {
        "username": username,
        "password": password
    }
    
    response = api_request("POST", "/api/v1/staff/login", login_data)
    
    if response and response.status_code == 200:
        login_result = response.json()
        STAFF_JWT_TOKEN = login_result["access_token"]
        CURRENT_STAFF_ID = login_result["staff_id"]
        print(f"✅ 員工登入成功: {login_result['full_name']}")
        return True
    else:
        print(f"❌ 員工登入失敗: {response.text if response else 'Network error'}")
        return False

def demo_merchant_management():
    """演示商戶管理功能"""
    print_section("商戶管理演示")
    
    # 獲取商戶資訊
    print_subsection("獲取商戶事件")
    response = api_request("GET", "/api/v1/mgmt/events/", use_merchant_auth=True)
    
    if response and response.status_code == 200:
        events = response.json()
        print(f"✅ 獲取到 {len(events)} 個活動")
        for event in events[:3]:
            print(f"   - {event['name']} (ID: {event['id']})")
    else:
        print("❌ 獲取活動失敗")

def demo_staff_operations():
    """演示員工操作功能"""
    print_section("員工操作演示")
    
    # 獲取員工個人資料
    print_subsection("獲取員工個人資料")
    response = api_request("GET", "/api/v1/staff/me/profile", use_staff_auth=True)
    
    if response and response.status_code == 200:
        profile = response.json()
        print(f"✅ 員工資料: {profile['full_name']} ({profile['username']})")
    else:
        print("❌ 獲取員工資料失敗")
    
    # 獲取員工可管理的活動
    print_subsection("獲取員工可管理的活動")
    response = api_request("GET", "/api/v1/staff/me/events", use_staff_auth=True)
    
    if response and response.status_code == 200:
        events = response.json()
        print(f"✅ 員工可管理 {len(events)} 個活動")
        for event in events:
            print(f"   - {event['event_name']} (簽到權限: {event['can_checkin']})")
        return events
    else:
        print("❌ 獲取員工活動失敗")
        return []

def demo_checkin_operations(staff_events):
    """演示簽到操作功能"""
    print_section("簽到操作演示")
    
    if not staff_events:
        print("❌ 沒有可用的活動進行簽到演示")
        return
    
    event_id = staff_events[0]['event_id']
    event_name = staff_events[0]['event_name']
    
    print_subsection(f"獲取活動 {event_name} 的簽到記錄")
    response = api_request("GET", f"/api/v1/staff/checkin/logs/{event_id}", use_staff_auth=True)
    
    if response and response.status_code == 200:
        logs = response.json()
        print(f"✅ 獲取到 {len(logs)} 筆簽到記錄")
        for log in logs[:3]:
            print(f"   - 票券 ID {log['ticket_id']}, 簽到時間: {log['checkin_time'][:19]}")
    else:
        print("❌ 獲取簽到記錄失敗")

def demo_sync_operations():
    """演示離線同步功能"""
    print_section("離線簽到同步演示")
    
    # 測試空的同步請求
    print_subsection("測試空的同步請求")
    sync_data = {
        "event_id": 1,
        "checkins": []
    }
    
    response = api_request("POST", "/api/v1/staff/checkin/sync", sync_data, use_staff_auth=True)
    
    if response and response.status_code == 200:
        result = response.json()
        print(f"✅ 同步成功: {result['message']}")
    else:
        print(f"❌ 同步失敗: {response.text if response else 'Network error'}")
    
    # 測試包含資料的同步請求 (使用假的資料，會失敗但可以看到錯誤處理)
    print_subsection("測試包含資料的同步請求 (預期失敗)")
    sync_data = {
        "event_id": 1,
        "checkins": [
            {
                "ticket_id": 999,  # 不存在的票券
                "event_id": 1,
                "checkin_time": "2025-06-25T10:00:00",
                "client_timestamp": "2025-06-25T10:00:00Z"
            }
        ]
    }
    
    response = api_request("POST", "/api/v1/staff/checkin/sync", sync_data, use_staff_auth=True)
    
    if response:
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 同步成功: {result['message']}")
        else:
            print(f"⚠️  預期的錯誤: {response.json().get('detail', 'Unknown error')}")

def demo_ticket_management():
    """演示票券管理功能"""
    print_section("票券管理演示")
    
    # 搜尋票券
    print_subsection("搜尋票券")
    search_params = {
        "holder_name": "測試"
    }
    
    response = api_request("GET", "/api/v1/mgmt/tickets/search", use_merchant_auth=True)
    
    if response and response.status_code == 200:
        tickets = response.json()
        print(f"✅ 找到 {len(tickets)} 張票券")
        for ticket in tickets[:3]:
            print(f"   - {ticket['holder_name']}: {ticket['ticket_code']}")
    else:
        print("❌ 搜尋票券失敗")

def main():
    """主函數"""
    print("🎬 QR Check-in System 完整功能演示開始")
    
    # 設置認證
    if not setup_authentication():
        print("❌ 認證設置失敗，演示結束")
        return
    
    print(f"\n✅ 認證設置完成")
    print(f"📑 商戶 API Key: {MERCHANT_API_KEY[:20]}...")
    print(f"🔑 員工 JWT Token: {STAFF_JWT_TOKEN[:30]}...")
    
    # 等待用戶確認
    input("\n按 Enter 繼續演示...")
    
    # 依序執行各項演示
    demo_merchant_management()
    staff_events = demo_staff_operations()
    demo_checkin_operations(staff_events)
    demo_sync_operations()
    demo_ticket_management()
    
    print_section("演示完成")
    print("🎉 所有功能演示完成！")
    print("\n📋 重要提醒:")
    print("1. 確保資料庫中有測試數據 (執行 setup_multi_tenant.py)")
    print("2. 確保 API 服務正常運行")
    print("3. 離線同步 API 已經在 Swagger 文件中可見")
    print("4. 員工需要正確的 JWT token 才能使用簽到功能")

if __name__ == "__main__":
    main()
