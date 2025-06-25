#!/usr/bin/env python3
"""
測試 API 端點
"""
import requests
import json

base_url = "http://localhost:8000"

def test_staff_login():
    """測試員工登入"""
    url = f"{base_url}/api/v1/staff/login"
    data = {
        "username": "staff-1750647514@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"✅ 員工登入狀態: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 取得 token: {result.get('access_token', '')[:20]}...")
            return result.get('access_token')
        else:
            print(f"❌ 登入失敗: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登入錯誤: {e}")
        return None

def test_revoke_checkin(token):
    """測試撤銷簽到"""
    if not token:
        print("❌ 沒有 token，跳過撤銷簽到測試")
        return
        
    url = f"{base_url}/api/v1/staff/checkin/revoke"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"checkin_log_id": 5}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"✅ 撤銷簽到狀態: {response.status_code}")
        print(f"✅ 回應: {response.text}")
    except Exception as e:
        print(f"❌ 撤銷簽到錯誤: {e}")

if __name__ == "__main__":
    print("🔍 測試 API 端點...")
    token = test_staff_login()
    test_revoke_checkin(token)
