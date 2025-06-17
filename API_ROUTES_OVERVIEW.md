# QR Check-in System - API Routes Overview

## 🚀 API 架構總覽

QR Check-in System 提供了清晰分層的 API 架構，區分公開功能、商戶專用功能和管理功能。

## 📋 所有 API 端點清單

### 1. 👤 員工認證與管理 (`/api/staff/`)

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| POST | `/api/staff/verify` | 員工驗證（帳密或登入碼） | 無 |
| GET | `/api/staff/profile` | 獲取當前員工資料 | Staff Token |
| GET | `/api/staff/events` | 查詢員工可存取的活動列表 | Staff Token |

### 2. 🎫 票券公開功能 (`/api/tickets/`)

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| GET | `/api/tickets/{ticket_id}/qrcode` | 產生票券 QR Code | 無 |
| POST | `/api/tickets/verify` | 驗證票券（不核銷） | 無 |

### 3. ✅ 簽到功能 (`/api/checkin/`)

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| POST | `/api/checkin` | 執行簽到核銷 | Staff Token |

### 4. 🎯 活動管理 (`/api/events/`) - 商戶專用

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| GET | `/api/events` | 查詢活動列表 | API Key |
| GET | `/api/events/{event_id}` | 查詢單一活動資料 | API Key |
| GET | `/api/events/{event_id}/ticket-types` | 查詢活動票種 | API Key |
| POST | `/api/events` | 創建活動 | API Key |
| PATCH | `/api/events/ticket-types/{ticket_type_id}` | 更新票種資訊 | API Key |
| DELETE | `/api/events/ticket-types/{ticket_type_id}` | 刪除票種 | API Key |
| GET | `/api/events/{event_id}/offline-tickets` | 下載離線票券資料 | API Key + Staff Token |

### 5. 🎫 票券管理 (`/api/tickets-mgmt/`) - 商戶專用

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| GET | `/api/tickets-mgmt/{ticket_id}` | 查詢單一票券 | API Key |
| GET | `/api/tickets-mgmt` | 查詢活動票券清單 | API Key |
| POST | `/api/tickets-mgmt` | **創建單張票券** ⭐ | API Key |
| POST | `/api/tickets-mgmt/batch` | 批次創建票券 | API Key |
| PUT | `/api/tickets-mgmt/{ticket_id}` | 更新票券資訊 | API Key |
| DELETE | `/api/tickets-mgmt/{ticket_id}` | 刪除票券 | API Key |
| POST | `/api/tickets-mgmt/verify` | 驗證票券（多租戶安全） | API Key |

### 6. ✅ 簽到管理 (`/api/checkin-mgmt/`) - 商戶專用

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| POST | `/api/checkin-mgmt` | 執行簽到核銷（多租戶安全） | API Key + Staff Token |
| POST | `/api/checkin-mgmt/revoke` | 撤銷簽到記錄 | API Key + Staff Token |
| POST | `/api/checkin-mgmt/offline-sync` | 離線簽到記錄同步 | API Key + Staff Token |
| GET | `/api/checkin-mgmt/logs` | 查詢簽到記錄 | API Key |
| GET | `/api/checkin-mgmt/logs/{log_id}` | 查詢單筆簽到記錄 | API Key |

### 7. 🏢 商戶管理 (`/admin/merchants/`) - 僅超級管理員

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| POST | `/admin/merchants` | 創建商戶 | Admin Password |
| GET | `/admin/merchants` | 獲取商戶列表 | Admin Password |
| GET | `/admin/merchants/{merchant_id}` | 獲取商戶詳情 | Admin Password |
| POST | `/admin/merchants/{merchant_id}/api-keys` | 為商戶創建 API Key | Admin Password |
| GET | `/admin/merchants/{merchant_id}/api-keys` | 獲取商戶 API Keys | Admin Password |
| DELETE | `/admin/merchants/{merchant_id}/api-keys/{key_id}` | 撤銷 API Key | Admin Password |
| GET | `/admin/merchants/{merchant_id}/statistics` | 獲取商戶統計 | Admin Password |

## 🔐 認證方式說明

### 1. 無認證
- 用於公開功能，如票券 QR Code 生成、票券驗證等

### 2. Staff Token 認證
- 用於員工相關功能
- Header: `Authorization: Bearer <staff_token>`

### 3. API Key 認證（商戶專用）
```http
X-API-Key: qr_abc123def456...  # 商戶專屬 API Key
Staff-ID: 1                    # 員工 ID（某些端點需要）
```

### 4. 超級管理員認證
```http
X-Admin-Password: your-admin-password
```

## ⭐ 新增功能亮點

### 1. 票券 Description 欄位
所有票券現在支援 `description` 欄位，可存儲 JSON 格式的額外資訊：

```json
{
  "seat": "A-01",
  "zone": "VIP", 
  "entrance": "Gate A",
  "meal": "vegetarian",
  "accessibility": "wheelchair",
  "parking": "P1-123"
}
```

### 2. 單張票券創建 API
新增 `POST /api/tickets-mgmt` 端點，支援創建單張票券：

```json
{
  "event_id": 1,
  "ticket_type_id": 1,
  "holder_name": "王小明",
  "holder_email": "test@example.com",
  "holder_phone": "0912345678",
  "notes": "VIP 客戶",
  "description": "{\"seat\": \"A-01\", \"zone\": \"VIP\"}"
}
```

## 📊 Event 和 Ticket_Type 關係說明

### Event（活動）
- 代表一個活動/演出/會議等
- 包含活動名稱、描述、時間、地點等基本資訊
- 每個 Event 屬於一個 Merchant（商戶）

### Ticket_Type（票種）
- 代表該活動下的不同票券類型
- 例如：一般票、早鳥票、VIP票、學生票等
- 每種票種有自己的價格、配額、名稱
- 一個活動可以有多種票種

### 使用場景舉例
```
活動：「2025 春季音樂會」
├── 票種1：一般票（價格：1000元，配額：500張）
├── 票種2：VIP票（價格：2000元，配額：100張）
└── 票種3：學生票（價格：500元，配額：200張）
```

## 🚀 快速開始

### 1. 查看 API 文檔
```bash
# 啟動服務後訪問
http://localhost:8000/docs
```

### 2. 測試 API
```bash
# 使用測試套件
./test_suite.sh
```

### 3. 創建票券示例
```bash
curl -X POST "http://localhost:8000/api/tickets-mgmt" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: qr_testmerchant123_456789abcdef" \
  -H "Staff-ID: 1" \
  -d '{
    "event_id": 1,
    "ticket_type_id": 1,
    "holder_name": "測試用戶",
    "holder_email": "test@example.com",
    "description": "{\"seat\": \"A-01\", \"zone\": \"VIP\"}"
  }'
```

---

**QR Check-in System v2.0** - 企業級多租戶票券簽到解決方案 🎉
