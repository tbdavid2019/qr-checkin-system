#!/usr/bin/env python3
"""
測試票券配額強制執行功能
"""
import requests
import json
import sys
from datetime import datetime, timedelta

# API 配置
BASE_URL = "http://localhost:8000"
API_KEY = "qr_nHKyfE2YUa8SK5cxujEa1ERzpyqjsV3u"  # 從數據庫中獲取的有效 API Key
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def print_step(step_num, description):
    print(f"\n=== 步驟 {step_num}: {description} ===")

def print_result(success, message):
    status = "✅ 成功" if success else "❌ 失敗"
    print(f"{status}: {message}")

def create_event_with_quota(name, total_quota):
    """創建帶有總配額限制的活動"""
    event_data = {
        "name": name,
        "description": "測試配額強制執行",
        "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2)).isoformat(),
        "location": "測試地點",
        "total_quota": total_quota
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/mgmt/events",
                           headers=HEADERS,
                           json=event_data)
    
    if response.status_code in [200, 201]:
        event = response.json()
        print_result(True, f"活動已創建，ID: {event['id']}, 總配額: {total_quota}")
        return event
    else:
        print_result(False, f"活動創建失敗: {response.text}")
        return None

def create_ticket_type(event_id, name, quota):
    """創建票券類型"""
    ticket_type_data = {
        "event_id": event_id,
        "name": name,
        "description": "測試票券類型",
        "price": 100.0,
        "quota": quota
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/mgmt/events/{event_id}/ticket-types",
                           headers=HEADERS,
                           json=ticket_type_data)
    
    if response.status_code in [200, 201]:
        ticket_type = response.json()
        print_result(True, f"票券類型已創建，ID: {ticket_type['id']}, 配額: {quota}")
        return ticket_type
    else:
        print_result(False, f"票券類型創建失敗: {response.text}")
        return None

def create_single_ticket(event_id, ticket_type_id, attendee_name):
    """創建單張票券"""
    ticket_data = {
        "event_id": event_id,
        "ticket_type_id": ticket_type_id,
        "holder_name": attendee_name,
        "holder_email": f"{attendee_name.lower()}@test.com",
        "holder_phone": "0900000000"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/mgmt/tickets",
                           headers=HEADERS,
                           json=ticket_data)
    
    return response

def create_batch_tickets(event_id, ticket_type_id, count):
    """批量創建票券"""
    tickets_data = []
    for i in range(count):
        tickets_data.append({
            "event_id": event_id,
            "ticket_type_id": ticket_type_id,
            "holder_name": f"測試參與者{i+1}",
            "holder_email": f"test{i+1}@test.com",
            "holder_phone": "0900000000"
        })
    
    response = requests.post(f"{BASE_URL}/api/v1/mgmt/tickets/batch",
                           headers=HEADERS,
                           json={"tickets": tickets_data})
    
    return response

def get_event_tickets_count(event_id):
    """獲取活動的票券總數"""
    response = requests.get(f"{BASE_URL}/api/v1/mgmt/tickets?event_id={event_id}",
                          headers=HEADERS)
    
    if response.status_code == 200:
        tickets = response.json()
        return len(tickets)
    return 0

def main():
    print("🎫 開始測試票券配額強制執行功能")
    
    # 步驟1：創建有配額限制的活動
    print_step(1, "創建總配額為 3 張票券的活動")
    event = create_event_with_quota("配額測試活動", 3)
    if not event:
        sys.exit(1)
    
    event_id = event["id"]
    
    # 步驟2：創建票券類型
    print_step(2, "創建票券類型 (配額: 10)")
    ticket_type = create_ticket_type(event_id, "普通票", 10)
    if not ticket_type:
        sys.exit(1)
    
    ticket_type_id = ticket_type["id"]
    
    # 步驟3：創建第一張票券 (應該成功)
    print_step(3, "創建第一張票券")
    response = create_single_ticket(event_id, ticket_type_id, "參與者1")
    if response.status_code in [200, 201]:
        print_result(True, "第一張票券創建成功")
    else:
        print_result(False, f"第一張票券創建失敗: {response.text}")
        sys.exit(1)
    
    # 步驟4：創建第二張票券 (應該成功)
    print_step(4, "創建第二張票券")
    response = create_single_ticket(event_id, ticket_type_id, "參與者2")
    if response.status_code in [200, 201]:
        print_result(True, "第二張票券創建成功")
    else:
        print_result(False, f"第二張票券創建失敗: {response.text}")
        sys.exit(1)
    
    # 步驟5：創建第三張票券 (應該成功)
    print_step(5, "創建第三張票券")
    response = create_single_ticket(event_id, ticket_type_id, "參與者3")
    if response.status_code in [200, 201]:
        print_result(True, "第三張票券創建成功")
        current_count = get_event_tickets_count(event_id)
        print(f"📊 當前活動票券總數: {current_count}")
    else:
        print_result(False, f"第三張票券創建失敗: {response.text}")
        sys.exit(1)
    
    # 步驟6：嘗試創建第四張票券 (應該失敗 - 超出活動總配額)
    print_step(6, "嘗試創建第四張票券 (應該失敗)")
    response = create_single_ticket(event_id, ticket_type_id, "參與者4")
    if response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "超出活動總配額" in error_detail:
            print_result(True, f"正確拒絕創建: {error_detail}")
        else:
            print_result(False, f"錯誤訊息不正確: {error_detail}")
    else:
        print_result(False, f"應該失敗但成功了: {response.status_code}")
    
    # 步驟7：測試批量創建 (應該失敗)
    print_step(7, "嘗試批量創建 2 張票券 (應該失敗)")
    response = create_batch_tickets(event_id, ticket_type_id, 2)
    if response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "超出活動總配額" in error_detail:
            print_result(True, f"正確拒絕批量創建: {error_detail}")
        else:
            print_result(False, f"錯誤訊息不正確: {error_detail}")
    else:
        print_result(False, f"應該失敗但成功了: {response.status_code}")
    
    # 最終檢查
    final_count = get_event_tickets_count(event_id)
    print(f"\n📊 最終票券總數: {final_count}")
    
    if final_count == 3:
        print_result(True, "配額強制執行測試全部通過！")
        print("\n🎉 票券配額強制執行功能運作正常")
    else:
        print_result(False, f"最終票券數量不正確，應該是 3 張，實際是 {final_count} 張")

if __name__ == "__main__":
    main()