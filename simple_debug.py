#!/usr/bin/env python3
"""
簡化版配額調試腳本
"""
import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_PASSWORD = "secure-admin-password-123"

def main():
    print("🔍 開始調試配額功能")
    
    # 測試基本 API 連接
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ API 伺服器連接正常 (狀態碼: {response.status_code})")
    except Exception as e:
        print(f"❌ API 伺服器連接失敗: {e}")
        return
    
    # 創建商戶
    try:
        merchant_data = {
            "name": "調試商戶",
            "email": "debug@example.com",
            "description": "調試配額功能"
        }
        
        headers = {
            "X-Admin-Password": ADMIN_PASSWORD,
            "Content-Type": "application/json"
        }
        
        print("🏪 創建商戶...")
        response = requests.post(f"{BASE_URL}/admin/merchants", headers=headers, json=merchant_data)
        print(f"商戶創建回應: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            api_key = data['api_key']
            print(f"✅ 商戶創建成功，API Key: {api_key}")
            
            # 創建活動
            event_data = {
                "name": "調試活動",
                "description": "調試配額功能",
                "start_time": "2025-06-24T10:00:00",
                "end_time": "2025-06-24T12:00:00",
                "location": "調試地點",
                "total_quota": 2
            }
            
            api_headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
            
            print("🎪 創建活動...")
            response = requests.post(f"{BASE_URL}/api/v1/mgmt/events", headers=api_headers, json=event_data)
            print(f"活動創建回應: {response.status_code}")
            
            if response.status_code in [200, 201]:
                event = response.json()
                print(f"✅ 活動創建成功，ID: {event['id']}")
                print(f"📋 完整回應: {json.dumps(event, indent=2, ensure_ascii=False)}")
                
                # 檢查 total_quota 是否在回應中
                if 'total_quota' in event:
                    print(f"🎯 配額設定: {event['total_quota']}")
                else:
                    print("⚠️ 回應中缺少 total_quota 欄位")
            else:
                print(f"❌ 活動創建失敗: {response.text}")
            
        else:
            print(f"❌ 商戶創建失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
