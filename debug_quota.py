#!/usr/bin/env python3
"""
調試配額功能 - 檢查資料庫狀態
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
ADMIN_PASSWORD = "secure-admin-password-123"

def debug_quota_functionality():
    """調試配額功能"""
    try:
        print("🔍 調試配額功能 - 檢查資料庫狀態")
    
    # 1. 創建商戶
    merchant_data = {
        "name": f"調試商戶_{int(time.time())}",
        "email": f"debug_{int(time.time())}@example.com",
        "description": "調試配額功能"
    }
    
    headers = {
        "X-Admin-Password": ADMIN_PASSWORD,
        "Content-Type": "application/json"
    }
    
    print("1. 創建商戶...")
    response = requests.post(f"{BASE_URL}/admin/merchants", headers=headers, json=merchant_data)
    if response.status_code not in [200, 201]:
        print(f"❌ 商戶創建失敗: {response.status_code} - {response.text}")
        return
    
    merchant_data = response.json()
    api_key = merchant_data['api_key']
    print(f"✅ 商戶創建成功，API Key: {api_key}")
    
    # 2. 創建活動（明確設定 total_quota）
    event_data = {
        "name": f"調試活動_{int(time.time())}",
        "description": "調試配額功能",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
        "location": "調試地點",
        "total_quota": 2  # 明確設定為 2 張票券
    }
    
    api_headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    print("2. 創建活動（配額=2）...")
    response = requests.post(f"{BASE_URL}/api/v1/mgmt/events", headers=api_headers, json=event_data)
    if response.status_code not in [200, 201]:
        print(f"❌ 活動創建失敗: {response.status_code} - {response.text}")
        return
    
    event = response.json()
    event_id = event['id']
    print(f"✅ 活動創建成功，ID: {event_id}")
    print(f"📋 活動完整回應: {json.dumps(event, indent=2, ensure_ascii=False)}")
    
    # 3. 查詢活動詳情確認配額
    print("3. 查詢活動詳情...")
    response = requests.get(f"{BASE_URL}/api/v1/mgmt/events/{event_id}", headers=api_headers)
    if response.status_code == 200:
        event_detail = response.json()
        print(f"📋 活動詳情: {json.dumps(event_detail, indent=2, ensure_ascii=False)}")
        print(f"🎯 活動配額: {event_detail.get('total_quota', 'None')}")
    else:
        print(f"❌ 查詢活動詳情失敗: {response.status_code} - {response.text}")
    
    # 4. 創建票券類型
    ticket_type_data = {
        "name": "調試票券",
        "description": "調試用票券類型",
        "price": 100.0,
        "quota": 10
    }
    
    print("4. 創建票券類型...")
    response = requests.post(f"{BASE_URL}/api/v1/mgmt/events/{event_id}/ticket-types", 
                           headers=api_headers, json=ticket_type_data)
    if response.status_code not in [200, 201]:
        print(f"❌ 票券類型創建失敗: {response.status_code} - {response.text}")
        return
    
    ticket_type = response.json()
    ticket_type_id = ticket_type['id']
    print(f"✅ 票券類型創建成功，ID: {ticket_type_id}")
    
    # 5. 測試票券創建（應該成功創建 2 張，第 3 張失敗）
    for i in range(4):  # 嘗試創建 4 張票券
        print(f"5.{i+1} 創建第 {i+1} 張票券...")
        ticket_data = {
            "event_id": event_id,
            "ticket_type_id": ticket_type_id,
            "holder_name": f"持票人{i+1}",
            "holder_email": f"holder{i+1}@example.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/mgmt/tickets", 
                               headers=api_headers, json=ticket_data)
        
        if response.status_code in [200, 201]:
            ticket = response.json()
            print(f"✅ 第 {i+1} 張票券創建成功，ID: {ticket['id']}")
        else:
            print(f"❌ 第 {i+1} 張票券創建失敗: {response.status_code} - {response.text}")
            break
    
    # 6. 查詢最終票券數量
    print("6. 查詢最終票券數量...")
    response = requests.get(f"{BASE_URL}/api/v1/mgmt/tickets?event_id={event_id}", headers=api_headers)
    if response.status_code == 200:
        tickets = response.json()
        print(f"📊 最終票券總數: {len(tickets)}")
        if len(tickets) <= 2:
            print("✅ 配額限制正常工作！")
        else:
            print("❌ 配額限制未生效！")
    else:
        print(f"❌ 查詢票券失敗: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ 調試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        debug_quota_functionality()
    except Exception as e:
        print(f"❌ 腳本執行錯誤: {e}")
        import traceback
        traceback.print_exc()
