import requests
import datetime
import json

API_URL = "http://localhost:8000/api/v1/staff/checkin/sync"
JWT_TOKEN = "<請填入測試用JWT>"

def test_sync_offline_checkins():
    # 模擬兩筆離線簽到資料
    now = datetime.datetime.utcnow().isoformat()
    payload = {
        "event_id": 1,
        "checkins": [
            {"ticket_id": 101, "event_id": 1, "checkin_time": now, "client_timestamp": str(int(datetime.datetime.now().timestamp()))},
            {"ticket_id": 102, "event_id": 1, "checkin_time": now, "client_timestamp": str(int(datetime.datetime.now().timestamp()))}
        ]
    }
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    print("Status:", resp.status_code)
    print("Response:", resp.json())

if __name__ == "__main__":
    test_sync_offline_checkins()
