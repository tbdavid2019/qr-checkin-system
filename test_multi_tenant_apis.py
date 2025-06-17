#!/usr/bin/env python3
"""
多租戶 API 測試腳本
測試各種 API 是否正確支援多租戶隔離
"""

import requests
import json
from datetime import datetime, timedelta

# 測試配置
BASE_URL = "http://localhost:8000"
API_KEY = "db0d665cb28e6a58dfce3461b9d38ba1"  # 從 .env 取得

def test_api_endpoint(method, url, headers=None, json_data=None):
    """測試 API 端點"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=json_data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.content else None
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    """主測試函數"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("=== 多租戶 API 測試 ===")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    print()
    
    # 測試商戶列表
    print("1. 測試商戶列表 API")
    result = test_api_endpoint("GET", f"{BASE_URL}/api/merchants", headers)
    print(f"商戶列表: {result}")
    print()
    
    # 測試員工列表
    print("2. 測試員工列表 API")
    result = test_api_endpoint("GET", f"{BASE_URL}/api/staff-simple", headers)
    print(f"員工列表: {result}")
    print()
    
    # 測試活動列表
    print("3. 測試活動列表 API")
    result = test_api_endpoint("GET", f"{BASE_URL}/api/events", headers)
    print(f"活動列表: {result}")
    print()
    
    # 測試建立活動
    print("4. 測試建立活動 API")
    event_data = {
        "name": "測試活動",
        "description": "多租戶測試活動",
        "location": "測試地點",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat()
    }
    result = test_api_endpoint("POST", f"{BASE_URL}/api/events", headers, event_data)
    print(f"建立活動: {result}")
    
    if result.get("status_code") == 200 and result.get("response"):
        event_id = result["response"]["id"]
        print(f"建立的活動 ID: {event_id}")
        
        # 測試查詢活動詳情
        print("5. 測試查詢活動詳情 API")
        result = test_api_endpoint("GET", f"{BASE_URL}/api/events/{event_id}", headers)
        print(f"活動詳情: {result}")
        print()
        
        # 測試活動票券列表
        print("6. 測試活動票券列表 API")
        result = test_api_endpoint("GET", f"{BASE_URL}/api/tickets?event_id={event_id}", headers)
        print(f"票券列表: {result}")
        print()
    
    print("=== 測試完成 ===")

if __name__ == "__main__":
    main()
