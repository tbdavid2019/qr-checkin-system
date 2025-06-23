# QR Check-in System - API Routes Overview (重構後)

## 🚀 新 API 架構總覽

QR Check-in System 已完成大規模重構，提供清晰分層的多租戶 API 架構，明確區分超級管理員、商戶、員工、公開端點的權限。

## 📋 重構後 API 端點清單

### 1. � 超級管理員 API (`/admin/`)

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| POST | `/admin/merchants` | 創建新商戶 | X-Admin-Password |
| GET | `/admin/merchants` | 獲取商戶列表 | X-Admin-Password |
| GET | `/admin/merchants/{merchant_id}` | 獲取商戶詳情 | X-Admin-Password |
| PUT | `/admin/merchants/{merchant_id}` | 更新商戶資訊 | X-Admin-Password |
| DELETE | `/admin/merchants/{merchant_id}` | 刪除商戶 | X-Admin-Password |

### 2. 🏢 商戶管理 API (`/api/v1/mgmt/`)

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| **活動管理** | | | |
| GET | `/api/v1/mgmt/events` | 查詢商戶活動列表 | X-API-Key |
| POST | `/api/v1/mgmt/events` | 創建新活動 | X-API-Key |
| GET | `/api/v1/mgmt/events/{event_id}` | 查詢活動詳情 | X-API-Key |
| PUT | `/api/v1/mgmt/events/{event_id}` | 更新活動 | X-API-Key |
| DELETE | `/api/v1/mgmt/events/{event_id}` | 刪除活動 | X-API-Key |
| **票券管理** | | | |
| GET | `/api/v1/mgmt/tickets` | 查詢票券列表 | X-API-Key |
| POST | `/api/v1/mgmt/tickets` | 創建單張票券 | X-API-Key |
| POST | `/api/v1/mgmt/tickets/batch` | 批次創建票券 | X-API-Key |
| GET | `/api/v1/mgmt/tickets/{ticket_id}` | 查詢票券詳情 | X-API-Key |
| PUT | `/api/v1/mgmt/tickets/{ticket_id}` | 更新票券 | X-API-Key |
| DELETE | `/api/v1/mgmt/tickets/{ticket_id}` | 刪除票券 | X-API-Key |
| **員工管理** | | | |
| GET | `/api/v1/mgmt/staff` | 查詢員工列表 | X-API-Key |
| POST | `/api/v1/mgmt/staff` | 創建新員工 | X-API-Key |
| GET | `/api/v1/mgmt/staff/{staff_id}` | 查詢員工詳情 | X-API-Key |
| PUT | `/api/v1/mgmt/staff/{staff_id}` | 更新員工資訊 | X-API-Key |
| DELETE | `/api/v1/mgmt/staff/{staff_id}` | 刪除員工 | X-API-Key |
| POST | `/api/v1/mgmt/staff/events/assign` | 指派員工到活動 | X-API-Key |
| DELETE | `/api/v1/mgmt/staff/events/unassign` | 移除員工活動權限 | X-API-Key |

### 3. 👤 員工操作 API (`/api/v1/staff/`)

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| POST | `/api/v1/staff/login` | 員工登入 | 無 |
| GET | `/api/v1/staff/profile` | 獲取員工個人資料 | JWT Token |
| GET | `/api/v1/staff/events` | 查詢可存取的活動 | JWT Token |
| **簽到功能** | | | |
| POST | `/api/v1/staff/checkin/` | 執行票券簽到 | JWT Token |
| POST | `/api/v1/staff/checkin/revoke` | 撤銷簽到記錄 | JWT Token |
| GET | `/api/v1/staff/checkin/logs/{event_id}` | 查詢活動簽到記錄 | JWT Token |

### 4. � 公開端點 API (`/api/v1/public/`)

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| GET | `/api/v1/public/tickets/{ticket_uuid}` | 查詢公開票券資訊 | 無 |
| GET | `/api/v1/public/tickets/{ticket_uuid}/qr-token` | 獲取 QR Token | 無 |
| GET | `/api/v1/public/tickets/{ticket_uuid}/qr` | 生成 QR Code 圖片 | 無 |

### 5. 🔧 系統端點

| 方法 | 端點 | 功能 | 認證需求 |
|------|------|------|----------|
| GET | `/health` | 服務健康檢查 | 無 |
| GET | `/docs` | API 文檔 (Swagger) | 無 |
| GET | `/redoc` | API 文檔 (ReDoc) | 無 |

## 🔐 認證方式說明

### 1. 超級管理員認證
```http
X-Admin-Password: secure-admin-password-123
```
- 用於 `/admin/*` 端點
- 創建和管理商戶

### 2. 商戶 API Key 認證
```http
X-API-Key: qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE
```
- 用於 `/api/v1/mgmt/*` 端點
- 商戶專屬功能（活動、票券、員工管理）

### 3. 員工 JWT 認證
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- 用於 `/api/v1/staff/*` 端點
- 員工登入後獲得的 JWT Token

### 4. 公開端點
- `/api/v1/public/*` 端點無需認證
- 用於票券資訊查詢和 QR Code 生成

## 🧪 測試帳密與 API Key

### 系統管理員
- **Admin Password**: `secure-admin-password-123`
- **用途**: 創建和管理商戶

### 測試商戶 API Key (最新)
- **API Key**: `qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE`
- **商戶 ID**: 53
- **用途**: 商戶管理功能測試

### 測試員工帳號 (最新)
- **用戶名**: `staff-1750647514@test.com`
- **密碼**: `password123`
- **員工 ID**: 50
- **用途**: 員工登入和簽到功能測試

### 測試活動與票券 (最新)
- **活動 ID**: 46
- **活動名稱**: 商戶核心測試活動
- **票券 UUID**: `98a82c23-f65e-4003-abbf-0c4729d047dd`
- **票券持有人**: 王大明

## 📝 API 使用範例

### 1. 創建商戶
```bash
curl -X POST "http://localhost:8000/admin/merchants" \
  -H "X-Admin-Password: secure-admin-password-123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "測試商戶",
    "email": "test@example.com",
    "description": "這是一個測試商戶"
  }'
```

### 2. 創建活動
```bash
curl -X POST "http://localhost:8000/api/v1/mgmt/events" \
  -H "X-API-Key: qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "測試活動",
    "start_date": "2025-06-23T10:00:00",
    "end_date": "2025-06-23T18:00:00",
    "location": "測試地點"
  }'
```

### 3. 創建員工
```bash
curl -X POST "http://localhost:8000/api/v1/mgmt/staff" \
  -H "X-API-Key: qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "staff@test.com",
    "password": "password123",
    "email": "staff@test.com",
    "full_name": "測試員工"
  }'
```

### 4. 員工登入
```bash
curl -X POST "http://localhost:8000/api/v1/staff/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "staff-1750647514@test.com",
    "password": "password123"
  }'
```

### 5. 創建票券
```bash
curl -X POST "http://localhost:8000/api/v1/mgmt/tickets" \
  -H "X-API-Key: qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 46,
    "holder_name": "王大明",
    "holder_email": "ming@test.com"
  }'
```

### 6. 票券簽到
```bash
curl -X POST "http://localhost:8000/api/v1/staff/checkin/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "qr_token": "YOUR_QR_TOKEN",
    "event_id": 46
  }'
```

## ⚠️ 重要安全提醒

1. **生產環境**: 請務必更改預設的 Admin Password
2. **API Key**: 定期輪換商戶 API Key
3. **JWT Token**: Token 有效期為 8 小時
4. **QR Token**: QR Token 有效期為 5 分鐘
5. **HTTPS**: 生產環境務必使用 HTTPS

## 🚀 快速測試

執行完整的自動化測試：
```bash
bash test_api_auth.sh
```

此腳本會測試：
- ✅ 服務健康檢查
- ✅ 超級管理員操作
- ✅ 商戶管理操作
- ✅ 員工操作
- ✅ 票券創建與簽到
- ✅ 公開端點
- ✅ 認證安全測試

---

**QR Check-in System v2.0** - 企業級多租戶票券簽到解決方案 🎉
