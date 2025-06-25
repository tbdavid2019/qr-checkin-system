# QR Check-in System 部署指南

本文件說明如何在新機器上部署 QR Check-in System，並確保所有腳本與新的多租戶架構同步。

## 重要更新

系統已升級為多租戶架構，並修正了以下重要問題：

1. **JWT 認證修正**: 員工 JWT token 現在包含 `type: 'staff'` 欄位
2. **離線同步 API**: `/api/v1/staff/checkin/sync` 現已正確顯示在 Swagger 文件中
3. **部署腳本更新**: 提供了新的多租戶版本的部署腳本

## 檔案說明

### 舊版檔案 (單租戶架構) - 不建議使用
- `create_test_data.py` - 舊版測試數據創建腳本
- `demo_complete_system.py` - 舊版功能演示腳本

### 新版檔案 (多租戶架構) - 推薦使用
- `create_test_data_new.py` - 新版測試數據創建腳本
- `demo_complete_system_new.py` - 新版功能演示腳本
- `setup_multi_tenant.py` - 多租戶設置腳本 (已更新)

## 部署步驟

### 1. 環境準備
```bash
# 克隆代碼庫
git clone <repository-url>
cd qr-checkin-system

# 確保 Docker 和 Docker Compose 已安裝
docker --version
docker-compose --version
```

### 2. 啟動服務
```bash
# 啟動資料庫和 API 服務
docker-compose up -d

# 等待服務完全啟動
sleep 30
```

### 3. 資料庫初始化
```bash
# 執行 migration
docker exec qr-checkin-system-api-1 alembic upgrade head

# 或者如果容器內執行失敗，可以本地執行
# alembic upgrade head
```

### 4. 創建測試數據
有兩種方式創建測試數據：

#### 方式 A: 使用多租戶設置腳本 (推薦)
```bash
python setup_multi_tenant.py
```

#### 方式 B: 使用新版測試數據腳本
```bash
python create_test_data_new.py
```

### 5. 驗證部署
```bash
# 檢查 API 健康狀態
curl http://localhost:8000/health

# 查看 Swagger 文件 (確認 sync API 存在)
curl http://localhost:8000/docs

# 執行功能演示
python demo_complete_system_new.py
```

## 重要變更說明

### JWT 認證修正
員工登入後獲得的 JWT token 現在包含正確的 `type` 欄位：
```json
{
  "sub": "1",
  "type": "staff",
  "exp": 1234567890
}
```

這確保了員工可以正確使用需要認證的 API，包括新的離線同步 API。

### 離線同步 API
`/api/v1/staff/checkin/sync` API 現已正確顯示在 Swagger 文件中，使用方式：

```bash
POST /api/v1/staff/checkin/sync
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "event_id": 1,
  "checkins": [
    {
      "ticket_id": 4,
      "event_id": 1,
      "checkin_time": "2025-06-25T10:00:00",
      "client_timestamp": "2025-06-25T10:00:00Z"
    }
  ]
}
```

### 多租戶架構
系統現在支援多個商戶，每個商戶有：
- 獨立的 API Key
- 獨立的員工和活動
- 隔離的數據存取權限

## 故障排除

### Migration 錯誤
如果遇到 alembic migration 錯誤，請：
1. 檢查是否有重複或損壞的 migration 檔案
2. 確保資料庫連線正常
3. 重新執行 `alembic upgrade head`

### API 認證問題
如果員工 API 回傳 401 錯誤：
1. 確認 JWT token 包含 `type: 'staff'` 欄位
2. 檢查 token 是否過期
3. 確認使用正確的 Authorization header 格式

### Swagger 文件問題
如果 sync API 未顯示在 Swagger 中：
1. 檢查 `routers/checkin.py` 是否有中文註釋
2. 重建 Docker 容器：`docker-compose build api && docker-compose up -d api`
3. 清除瀏覽器快取後重新載入 Swagger 頁面

## 聯絡支援
如果在部署過程中遇到問題，請提供：
1. 錯誤訊息的完整輸出
2. Docker 容器日誌：`docker logs qr-checkin-system-api-1`
3. 使用的作業系統和 Docker 版本
