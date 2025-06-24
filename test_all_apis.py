#!/usr/bin/env python3
"""
測試所有問題 API
"""
import requests
import json
import random

base_url = "http://localhost:8000"
merchant_api_key = "qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a" # 使用從資料庫查到的金鑰

def get_staff_token():
    """獲取員工 token"""
    url = f"{base_url}/api/v1/staff/login"
    data = {
        "username": "staff-1750647514@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            return response.json().get('access_token')
    except Exception as e:
        print(f"❌ 獲取 token 失敗: {e}")
    return None

def test_api(name, method, url, headers=None, data=None, params=None):
    """通用 API 測試函數"""
    print(f"\n🔍 測試 {name}")
    print(f"   URL: {url}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        print(f"   狀態: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ 成功!")
            # 只顯示回應的前200個字符
            response_text = response.text
            if len(response_text) > 200:
                response_text = response_text[:200] + "..."
            print(f"   回應: {response_text}")
        else:
            print(f"   ❌ 失敗!")
            print(f"   錯誤: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 請求錯誤: {e}")

def main():
    print("🔍 測試所有問題 API 端點...")
    
    # 獲取認證 token
    staff_token = get_staff_token()
    staff_headers = {"Authorization": f"Bearer {staff_token}"} if staff_token else {}
    merchant_headers = {"X-API-Key": merchant_api_key}
    
    # 1. 撤銷簽到記錄 API
    test_api(
        "撤銷簽到記錄 API",
        "POST",
        f"{base_url}/api/v1/staff/checkin/revoke",
        headers=staff_headers,
        data={"checkin_log_id": 5}
    )
    
    # 測試 更新票種資訊 API
    update_ticket_type_id = 3 # 使用從資料庫查到的 ID
    test_api(
        "更新票種資訊 API",
        "PUT",
        f"{base_url}/api/v1/mgmt/events/ticket-types/{update_ticket_type_id}",
        headers={"X-API-Key": merchant_api_key},
        data={"name": "超級優待票", "price": 999.99}
    )

    # 為了測試刪除，先建立一個新票種
    event_id_for_new_ticket_type = 1 # 從資料庫查到的活動 ID
    new_ticket_type_name = f"待刪除票種_{random.randint(1000, 9999)}"
    response = test_api(
        "建立待刪除票種",
        "POST",
        f"{base_url}/api/v1/mgmt/events/{event_id_for_new_ticket_type}/ticket-types",
        headers={"X-API-Key": merchant_api_key},
        data={"name": new_ticket_type_name, "price": 10.0, "quota": 100}
    )

    # 測試 刪除票種 API
    if response and response.status_code == 200:
        delete_ticket_type_id = response.json().get('id')
        test_api(
            "刪除新建票種 API",
            "DELETE",
            f"{base_url}/api/v1/mgmt/events/ticket-types/{delete_ticket_type_id}",
            headers={"X-API-Key": merchant_api_key}
        )

    # 測試 獲取活動摘要 API
    event_id_for_summary = 1 # 從資料庫查到的活動 ID
    test_api(
        "獲取活動摘要 API",
        "GET",
        f"{base_url}/api/v1/mgmt/events/{event_id_for_summary}/summary",
        headers={"X-API-Key": merchant_api_key}
    )

    # 測試 透過持有人搜尋票券 API
    test_api(
        "透過持有人搜尋票券 API",
        "GET",
        f"{base_url}/api/v1/mgmt/tickets/search/by-holder",
        headers=merchant_headers,
        params={"email": "test@example.com"}
    )
    
    # 6. 負數分頁偏移測試
    test_api(
        "負數分頁偏移測試",
        "GET",
        f"{base_url}/api/v1/mgmt/events",
        headers=merchant_headers,
        params={"skip": -1, "limit": 10}
    )

if __name__ == "__main__":
    main()
