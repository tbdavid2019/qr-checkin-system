# QR Check-in System API 測試說明

這個目錄包含了完整的 API 測試套件，用於驗證 QR Check-in System 的所有功能。

## 📋 測試腳本清單

### 🚀 主要測試腳本

1. **`test_suite.sh`** - 測試套件主選單
   - 互動式選單，包含所有測試選項
   - 服務狀態檢查
   - API 文檔連結

2. **`test_real_apis.sh`** - 真實 API 完整測試
   - 使用資料庫中真實的 API Key
   - 測試所有主要功能模組
   - 包含商戶、活動、員工、票券、簽到等

3. **`test_api_quick.sh`** - 快速 API 測試
   - 基本端點測試
   - 適合快速驗證服務狀態

4. **`test_api_auth.sh`** - 認證機制測試
   - 測試 API 認證流程
   - 驗證權限控制

5. **`test_complete_apis.sh`** - 完整 API 測試
   - 基於 OpenAPI 規範的全面測試
   - 包含錯誤處理和邊界測試

6. **`test_multi_tenant_apis.py`** - 多租戶功能測試
   - Python 腳本，測試多租戶資料隔離
   - 驗證跨商戶權限控制

## 🔧 使用方法

### 快速開始

```bash
# 執行測試套件主選單
./test_suite.sh

# 或直接執行特定測試
./test_real_apis.sh
```

### 個別測試腳本

```bash
# 快速測試
./test_api_quick.sh

# 認證測試
./test_api_auth.sh

# 真實數據測試
./test_real_apis.sh

# 完整測試
./test_complete_apis.sh

# 多租戶測試
python3 test_multi_tenant_apis.py
```

## 🔑 認證資訊

### API Keys

- **管理員 API Key**: `db0d665cb28e6a58dfce3461b9d38ba1`
- **商戶 API Key**: `qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a` (台北演唱會公司)
- **員工 ID**: `1`

### 使用範例

```bash
# 商戶管理 (需要管理員權限)
curl -H "X-API-Key: db0d665cb28e6a58dfce3461b9d38ba1" \
     http://localhost:8000/admin/merchants

# 員工操作 (需要商戶 API Key + 員工 ID)
curl -H "X-API-Key: qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a" \
     -H "Staff-Id: 1" \
     http://localhost:8000/api/events

# 票券驗證
curl -H "X-API-Key: qr_uaIPi98rFvDQqUpPeBqePwZGwVr3jJ5a" \
     -H "Content-Type: application/json" \
     -d '{"ticket_id": "TICKET_001"}' \
     http://localhost:8000/admin/api/tickets/verify
```

## 🌐 服務端點

- **API 服務**: http://localhost:8000
- **Swagger 文檔**: http://localhost:8000/docs
- **Gradio 管理介面**: http://localhost:7860
- **健康檢查**: http://localhost:8000/health

## 📊 測試涵蓋範圍

### 功能模組

- ✅ **基礎 API**: 根路由、健康檢查、文檔
- ✅ **商戶管理**: CRUD 操作、統計、API Key 管理
- ✅ **活動管理**: 活動列表、詳情、票券類型
- ✅ **員工管理**: 員工 CRUD、權限驗證
- ✅ **票券管理**: 票券 CRUD、驗證、QR Code
- ✅ **簽到管理**: 簽到記錄、統計、日誌
- ✅ **匯出功能**: 票券匯出、簽到記錄匯出
- ✅ **多租戶**: 資料隔離、跨商戶權限

### 安全測試

- ✅ **認證機制**: API Key 驗證
- ✅ **權限控制**: 角色別權限檢查
- ✅ **資料隔離**: 多租戶資料分離
- ✅ **錯誤處理**: 無效請求處理

## 🐛 故障排除

### 常見問題

1. **API 無法連線**
   ```bash
   # 檢查 Docker 容器狀態
   docker-compose ps
   
   # 重啟服務
   docker-compose restart
   ```

2. **認證失敗**
   ```bash
   # 檢查 API Key 是否正確
   curl -H "X-API-Key: db0d665cb28e6a58dfce3461b9d38ba1" \
        http://localhost:8000/admin/merchants
   ```

3. **資料庫連線問題**
   ```bash
   # 檢查資料庫狀態
   docker exec qr-checkin-system-db-1 pg_isready -U qr_admin
   ```

### 測試失敗處理

1. **檢查服務狀態**
   ```bash
   ./test_suite.sh
   # 選擇選項 7: 檢查服務狀態
   ```

2. **查看錯誤日誌**
   ```bash
   docker-compose logs api
   docker-compose logs db
   ```

3. **重新建置服務**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## 📝 測試結果

測試執行後會在以下位置生成日誌：
- `/tmp/quick_test.log` - 快速測試日誌
- `/tmp/auth_test.log` - 認證測試日誌
- `/tmp/real_test.log` - 真實 API 測試日誌
- `/tmp/multi_tenant_test.log` - 多租戶測試日誌

## 🔄 持續整合

這些測試腳本可以整合到 CI/CD 流程中：

```bash
# CI 腳本範例
#!/bin/bash
set -e

# 啟動服務
docker-compose up -d

# 等待服務啟動
sleep 30

# 執行所有測試
./test_real_apis.sh
python3 test_multi_tenant_apis.py

# 清理
docker-compose down
```

---

**注意**: 確保在執行測試前，所有 Docker 容器都已正常啟動並且服務可以正常存取。
