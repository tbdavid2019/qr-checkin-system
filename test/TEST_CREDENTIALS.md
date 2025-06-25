# 🧪 測試憑證與帳密資訊

## 📋 系統帳密總覽

這份文檔包含了測試環境中所有可用的帳密、API Key 和測試資料。

## 🔐 認證憑證

### 1. 超級管理員
```
Admin Password: secure-admin-password-123
```
**用途**: 
- 創建和管理商戶
- 存取 `/admin/*` 端點

**測試端點**:
```bash
# 創建商戶
curl -X POST "http://localhost:8000/admin/merchants" \
  -H "X-Admin-Password: secure-admin-password-123" \
  -H "Content-Type: application/json" \
  -d '{"name": "測試商戶", "email": "test@example.com"}'
```

### 2. 商戶 API Key (自動化測試生成)
```
最新 API Key: qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE
商戶 ID: 53
商戶名稱: 測試商戶1750647514
```

**用途**: 
- 商戶管理功能（活動、票券、員工）
- 存取 `/api/v1/mgmt/*` 端點

### 3. 員工帳號 (自動化測試生成)
```
用戶名: staff-1750647514@test.com
密碼: password123
員工 ID: 50
姓名: 測試員工
```

**JWT Token 範例**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MCIsImV4cCI6MTc1MDY3NjM1OSwidHlwZSI6ImFjY2Vzc190b2tlbiJ9.xxx
```

## 🎯 測試資料

### 活動資訊
```
活動 ID: 46
活動名稱: 商戶核心測試活動
開始時間: 2025-06-23T10:00:00
結束時間: 2025-06-23T18:00:00
地點: 測試地點
```

### 票券資訊
```
票券 ID: 69
票券 UUID: 98a82c23-f65e-4003-abbf-0c4729d047dd
票券代碼: 63RCJ0MX9MXK
持有人: 王大明
Email: ming@test.com
狀態: 已使用 (已簽到)
```

### QR Token 範例
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0aWNrZXRfdXVpZCI6Ijk4YTgyYzIzLWY2NWUtNDAwMy1hYmJmLTBjNDcyOWQwNDdkZCIsImV2ZW50X2lkIjo0NiwiZXhwIjoxNzUxMjUyMzE5LCJ0eXBlIjoicXJfdG9rZW4ifQ.bung7CV7eblI_LZ8faS33zyYF6MPfoTP2hh5yogyItY
```

## 🔄 動態憑證資訊

由於測試會動態生成新的憑證，以下是最新的測試執行結果：

### 最後一次成功測試 (2025-06-23 02:58:39)
- **商戶 ID**: 53
- **API Key**: `qr_EKoHBUDPnRtnonUUrWFeB9vExlWjSXGE`
- **員工 ID**: 50
- **員工用戶名**: `staff-1750647514@test.com`
- **活動 ID**: 46
- **票券 UUID**: `98a82c23-f65e-4003-abbf-0c4729d047dd`

## 📱 完整測試流程

### 1. 啟動服務
```bash
docker-compose up -d
```

### 2. 執行自動化測試
```bash
bash test_api_auth.sh
```

### 3. 手動測試範例

#### 步驟 1: 創建商戶
```bash
curl -X POST "http://localhost:8000/admin/merchants" \
  -H "X-Admin-Password: secure-admin-password-123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的測試商戶",
    "email": "my-test@example.com",
    "description": "手動創建的測試商戶"
  }'
```

#### 步驟 2: 創建活動 (使用上步驟返回的 API Key)
```bash
curl -X POST "http://localhost:8000/api/v1/mgmt/events" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的測試活動",
    "start_date": "2025-06-23T14:00:00",
    "end_date": "2025-06-23T18:00:00",
    "location": "台北市信義區"
  }'
```

#### 步驟 3: 創建員工
```bash
curl -X POST "http://localhost:8000/api/v1/mgmt/staff" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mystaff@test.com",
    "password": "mypassword123",
    "email": "mystaff@test.com",
    "full_name": "我的測試員工"
  }'
```

#### 步驟 4: 指派員工到活動
```bash
curl -X POST "http://localhost:8000/api/v1/mgmt/staff/events/assign" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "staff_id": YOUR_STAFF_ID,
    "event_id": YOUR_EVENT_ID,
    "can_checkin": true,
    "can_revoke": false
  }'
```

#### 步驟 5: 員工登入
```bash
curl -X POST "http://localhost:8000/api/v1/staff/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mystaff@test.com",
    "password": "mypassword123"
  }'
```

#### 步驟 6: 創建票券
```bash
curl -X POST "http://localhost:8000/api/v1/mgmt/tickets" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": YOUR_EVENT_ID,
    "holder_name": "張三",
    "holder_email": "zhang@test.com"
  }'
```

#### 步驟 7: 獲取 QR Token
```bash
curl -X GET "http://localhost:8000/api/v1/public/tickets/YOUR_TICKET_UUID/qr-token"
```

#### 步驟 8: 簽到
```bash
curl -X POST "http://localhost:8000/api/v1/staff/checkin/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "qr_token": "YOUR_QR_TOKEN",
    "event_id": YOUR_EVENT_ID
  }'
```

## 🔍 查詢公開票券資訊
```bash
curl -X GET "http://localhost:8000/api/v1/public/tickets/98a82c23-f65e-4003-abbf-0c4729d047dd"
```

回應範例:
```json
{
  "uuid": "98a82c23-f65e-4003-abbf-0c4729d047dd",
  "holder_name": "王大明",
  "is_used": true,
  "event_id": 46,
  "ticket_type_id": null,
  "description": null
}
```

## 📊 API 文檔

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康檢查**: http://localhost:8000/health

## ⚠️ 注意事項

1. **動態憑證**: 每次執行測試都會生成新的憑證
2. **Token 有效期**: 
   - JWT Token: 8 小時
   - QR Token: 5 分鐘
3. **資料庫**: 使用 Docker PostgreSQL，重啟後資料保留
4. **多租戶**: 確保不同商戶的資料完全隔離
5. **權限驗證**: 員工只能操作被指派的活動
