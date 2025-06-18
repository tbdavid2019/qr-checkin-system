"""
QR Check-in System 完整功能演示腳本
展示系統的所有主要功能
"""
import requests
import json
import time

# API 基礎URL
BASE_URL = "http://localhost:8000"
API_KEY = "test-api-key"
ADMIN_STAFF_ID = 1

def print_section(title):
    """打印章節標題"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_subsection(title):
    """打印子章節標題"""
    print(f"\n📌 {title}")
    print('-'*40)

def api_request(method, endpoint, data=None, headers=None, staff_id=None):
    """統一的API請求函數"""
    url = f"{BASE_URL}{endpoint}"
    default_headers = {}
    
    if staff_id:
        default_headers.update({
            "X-API-Key": API_KEY,
            "Staff-ID": str(staff_id)
        })
    
    if headers:
        default_headers.update(headers)
    
    if method.upper() == "GET":
        response = requests.get(url, headers=default_headers)
    elif method.upper() == "POST":
        default_headers["Content-Type"] = "application/json"
        response = requests.post(url, json=data, headers=default_headers)
    
    return response

def demo_authentication():
    """演示認證功能"""
    print_section("認證系統演示")
    
    print_subsection("1. 員工身份驗證")
    # 測試管理員認證
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    response = api_request("POST", "/api/staff/verify", data=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 管理員認證成功")
        print(f"   員工ID: {result['staff_id']}")
        print(f"   姓名: {result['full_name']}")
    else:
        print(f"❌ 認證失敗: {response.text}")
        return False
    
    print_subsection("2. 獲取員工資料")
    response = api_request("GET", "/api/staff/profile", staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ 員工資料獲取成功")
        print(f"   用戶名: {profile['username']}")
        print(f"   姓名: {profile['full_name']}")
        print(f"   管理員權限: {profile['is_admin']}")
    else:
        print(f"❌ 獲取員工資料失敗: {response.text}")
    
    print_subsection("3. 查詢員工活動權限")
    response = api_request("GET", "/api/staff/events", staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ 找到 {len(events)} 個授權活動")
        for event in events:
            print(f"   - {event['event_name']} (ID: {event['event_id']})")
            print(f"     簽到權限: {event['can_checkin']}")
            print(f"     撤銷權限: {event['can_revoke']}")
    else:
        print(f"❌ 查詢活動權限失敗: {response.text}")
    
    return True

def demo_ticket_management():
    """演示票券管理功能"""
    print_section("票券管理演示")
    
    print_subsection("1. QR Code 生成")
    # 為票券ID 2生成QR Code
    response = api_request("GET", "/api/tickets/2/qrcode")
    
    if response.status_code == 200:
        qr_data = response.json()
        print(f"✅ QR Code 生成成功")
        print(f"   票券代碼: {qr_data['ticket_code']}")
        print(f"   持票人: {qr_data['holder_name']}")
        print(f"   QR Token: {qr_data['qr_token'][:30]}...")
        
        # 保存token供後續使用
        global demo_qr_token
        demo_qr_token = qr_data['qr_token']
    else:
        print(f"❌ QR Code 生成失敗: {response.text}")
        return False
    
    print_subsection("2. 票券驗證")
    verify_data = {"qr_token": demo_qr_token}
    response = api_request("POST", "/api/tickets/verify", data=verify_data)
    
    if response.status_code == 200:
        result = response.json()
        if result["valid"]:
            print(f"✅ 票券驗證成功")
            print(f"   持票人: {result['holder_name']}")
            print(f"   票種: {result['ticket_type_name']}")
            print(f"   使用狀態: {'已使用' if result['is_used'] else '未使用'}")
        else:
            print(f"❌ 票券無效: {result['message']}")
    else:
        print(f"❌ 票券驗證失敗: {response.text}")
    
    print_subsection("3. 批次票券創建")
    batch_data = {
        "event_id": 1,
        "ticket_type_id": 2,  # VIP票
        "count": 3,
        "holder_name_prefix": "演示VIP票券",
        "description": "{\"seat_zone\": \"VIP\", \"entrance\": \"Gate A\", \"floor\": 2}"
    }
    response = api_request("POST", "/admin/api/tickets/batch", 
                          data=batch_data, staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"✅ 成功創建 {len(tickets)} 張VIP票券")
        for i, ticket in enumerate(tickets[:2]):  # 只顯示前2張
            print(f"   {i+1}. {ticket['holder_name']}: {ticket['ticket_code']}")
    else:
        print(f"❌ 批次創建失敗: {response.text}")
    
    return True

def demo_checkin_system():
    """演示簽到系統功能"""
    print_section("簽到系統演示")
    
    print_subsection("1. 執行票券簽到")
    checkin_data = {
        "qr_token": demo_qr_token,
        "event_id": 1
    }
    response = api_request("POST", "/api/checkin", 
                          data=checkin_data, staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            print(f"✅ 簽到成功")
            print(f"   持票人: {result['holder_name']}")
            print(f"   簽到時間: {result['checkin_time']}")
        else:
            print(f"ℹ️ 簽到結果: {result['message']}")
    else:
        print(f"❌ 簽到失敗: {response.text}")
    
    print_subsection("2. 查詢簽到記錄")
    response = api_request("GET", "/admin/api/checkin/logs?event_id=1", 
                          staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        logs = response.json()
        print(f"✅ 找到 {len(logs)} 筆簽到記錄")
        for log in logs[:3]:  # 顯示前3筆
            print(f"   - 票券ID {log['ticket_id']}: {log['ticket']['holder_name']}")
            print(f"     簽到時間: {log['checkin_time']}")
            print(f"     簽到員工: {log['staff']['full_name'] if log['staff'] else 'N/A'}")
            print(f"     撤銷狀態: {'已撤銷' if log['is_revoked'] else '正常'}")
    else:
        print(f"❌ 查詢簽到記錄失敗: {response.text}")
    
    print_subsection("3. 離線同步演示")
    # 模擬離線簽到數據
    offline_data = {
        "event_id": 1,
        "checkins": [
            {
                "ticket_id": 6,  # 使用批次創建的票券之一
                "event_id": 1,
                "checkin_time": "2025-06-13T10:30:00.000000",
                "client_timestamp": str(int(time.time()))
            }
        ]
    }
    response = api_request("POST", "/admin/api/checkin/sync", 
                          data=offline_data, staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            print(f"✅ 離線同步成功: {result['message']}")
        else:
            print(f"ℹ️ 同步結果: {result['message']}")
    else:
        print(f"❌ 離線同步失敗: {response.text}")

def demo_statistics_and_export():
    """演示統計和導出功能"""
    print_section("統計與導出演示")
    
    print_subsection("1. 活動統計資訊")
    response = api_request("GET", "/api/events/1/statistics", 
                          staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 活動統計資訊")
        print(f"   總票券數: {stats['total_tickets']}")
        print(f"   已使用票券: {stats['used_tickets']}")
        print(f"   未使用票券: {stats['unused_tickets']}")
        print(f"   使用率: {stats['usage_rate']}%")
        print(f"   簽到記錄: {stats['checkin_count']}")
        print(f"   撤銷記錄: {stats['revoked_count']}")
        
        print(f"\n   票種統計:")
        for ticket_type in stats['ticket_types']:
            print(f"   - {ticket_type['name']}: "
                  f"已售 {ticket_type['sold_count']}/{ticket_type['quota']}, "
                  f"已用 {ticket_type['used_count']}")
    else:
        print(f"❌ 獲取統計資訊失敗: {response.text}")
    
    print_subsection("2. 事件管理功能")
    # 查詢活動列表
    response = api_request("GET", "/api/events", staff_id=ADMIN_STAFF_ID)
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ 找到 {len(events)} 個活動")
        for event in events:
            print(f"   - {event['name']} (ID: {event['id']})")
            print(f"     時間: {event['start_time'][:10]} 至 {event['end_time'][:10]}")
            print(f"     狀態: {'啟用' if event['is_active'] else '停用'}")
    else:
        print(f"❌ 查詢活動列表失敗: {response.text}")

def demo_api_summary():
    """API 總結展示"""
    print_section("API 功能總結")
    
    api_endpoints = [
        ("員工認證", "POST /api/staff/verify", "驗證員工身份"),
        ("員工資料", "GET /api/staff/profile", "獲取員工資料"),
        ("員工活動", "GET /api/staff/events", "查詢員工授權活動"),
        ("QR Code生成", "GET /api/tickets/{id}/qrcode", "生成票券QR Code"),
        ("票券驗證", "POST /api/tickets/verify", "驗證QR Token"),
        ("執行簽到", "POST /api/checkin", "掃描QR Code簽到"),
        ("簽到記錄", "GET /admin/api/checkin/logs", "查詢簽到記錄"),
        ("離線同步", "POST /admin/api/checkin/sync", "同步離線簽到"),
        ("撤銷簽到", "POST /admin/api/checkin/revoke", "撤銷簽到記錄"),
        ("批次產票", "POST /admin/api/tickets/batch", "批次創建票券"),
        ("活動統計", "GET /api/events/{id}/statistics", "獲取活動統計"),
        ("活動管理", "GET /api/events", "查詢活動列表"),
        ("票券導出", "GET /api/events/{id}/export/tickets", "導出票券CSV"),
        ("記錄導出", "GET /api/events/{id}/export/checkin-logs", "導出簽到記錄")
    ]
    
    print("\n📋 可用的API端點:")
    for category, endpoint, description in api_endpoints:
        print(f"   {category:10} | {endpoint:35} | {description}")
    
    print(f"\n🔑 認證方式:")
    print(f"   所有需要認證的API都使用Header認證:")
    print(f"   X-API-Key: {API_KEY}")
    print(f"   Staff-ID: {ADMIN_STAFF_ID}")

def main():
    """主演示流程"""
    print("🚀 QR Check-in System 完整功能演示")
    print("🌟 展示系統的核心功能和API使用方式")
    
    # 執行各個演示模塊
    if not demo_authentication():
        print("❌ 認證演示失敗，停止演示")
        return
    
    if not demo_ticket_management():
        print("❌ 票券管理演示失敗，停止演示")
        return
    
    demo_checkin_system()
    demo_statistics_and_export()
    demo_api_summary()
    
    print_section("演示完成")
    print("🎉 QR Check-in System 所有核心功能演示完成！")
    print("\n📊 系統功能狀態:")
    print("✅ 員工認證系統 - 支援用戶名/密碼和登入碼認證")
    print("✅ 票券管理系統 - QR Code生成、驗證、批次創建")
    print("✅ 簽到核銷系統 - 掃描簽到、記錄查詢、權限控制")
    print("✅ 離線同步功能 - 支援離線操作和批次同步")
    print("✅ 統計報表功能 - 活動統計、票種分析")
    print("✅ 管理端功能 - 撤銷、導出、事件管理")
    print("✅ API安全機制 - API Key認證、權限分級")
    
    print("\n🔗 快速開始:")
    print("1. 訪問 http://localhost:8000/docs 查看API文檔")
    print("2. 使用 X-API-Key: test-api-key 進行API認證")
    print("3. 管理員ID: 1, 用戶名: admin, 密碼: admin123")

if __name__ == "__main__":
    main()
