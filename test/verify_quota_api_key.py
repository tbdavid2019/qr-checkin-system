#!/usr/bin/env python3
"""
驗證 test_quota_enforcement.py 的 API Key 是否工作正常
"""
import requests
import json
import time
from datetime import datetime, timedelta

# API 配置
BASE_URL = "http://localhost:8000"
ADMIN_PASSWORD = "secure-admin-password-123"

def test_quota_api_key():
    """測試配額測試腳本的 API Key 功能"""
    print("🧪 測試配額強制執行腳本的 API Key 設定")
    
    # 創建商戶並獲取 API Key
    merchant_data = {
        "name": f"API Key驗證商戶_{int(time.time())}",
        "email": f"verify_{int(time.time())}@example.com",
        "description": "驗證API Key功能"
    }
    
    headers = {
        "X-Admin-Password": ADMIN_PASSWORD,
        "Content-Type": "application/json"
    }
    
    print("1. 創建商戶...")
    response = requests.post(f"{BASE_URL}/admin/merchants", headers=headers, json=merchant_data)
    
    if response.status_code in [200, 201]:
        data = response.json()
        api_key = data['api_key']
        print(f"✅ 商戶創建成功，API Key: {api_key}")
        
        # 測試 API Key 是否能創建活動
        print("2. 測試 API Key 創建活動...")
        event_data = {
            "name": f"API Key測試活動_{int(time.time())}",
            "description": "驗證API Key功能",
            "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
            "location": "測試地點"
        }
        
        api_headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/mgmt/events", headers=api_headers, json=event_data)
        
        if response.status_code in [200, 201]:
            event = response.json()
            print(f"✅ 活動創建成功，ID: {event['id']}")
            print("🎉 API Key 功能驗證成功！")
            return True
        else:
            print(f"❌ 活動創建失敗: {response.text}")
            return False
    else:
        print(f"❌ 商戶創建失敗: {response.text}")
        return False

if __name__ == "__main__":
    test_quota_api_key()
