# QR Check-in System 完成報告

## 📋 項目概覽

這是一個基於 FastAPI 的綜合性 QR Code 簽到系統，支援票券管理、員工認證、簽到核銷、離線同步等完整功能。

## ✅ 已完成功能

### 🔐 認證系統
- **簡化認證機制**: 使用 API Key + Staff ID 的 Header 認證方式
- **員工驗證**: 支援用戶名/密碼和登入碼兩種方式
- **權限控制**: 基於員工-活動關聯的權限管理系統

### 🎫 票券管理
- **票券創建**: 單張票券和批次票券創建
- **QR Code 生成**: JWT Token 為基礎的 QR Code 生成
- **票券驗證**: QR Token 驗證功能（不執行簽到）
- **票券查詢**: 根據活動、票券ID等查詢功能

### 🎯 簽到系統
- **QR Code 簽到**: 掃描 QR Code 進行票券核銷
- **重複檢查**: 防止重複簽到的安全機制
- **IP/User-Agent 記錄**: 記錄簽到來源資訊
- **簽到記錄查詢**: 完整的簽到歷史記錄管理

### 🔄 離線同步
- **離線簽到緩存**: 支援離線環境下的簽到記錄
- **批次同步**: 網路恢復後批次上傳離線簽到記錄
- **重複處理**: 智能處理重複簽到記錄

### 📊 管理功能
- **簽到撤銷**: 管理員可撤銷錯誤的簽到記錄
- **統計報表**: 活動統計、票種統計等功能
- **資料導出**: CSV 格式的簽到記錄和票券清單導出
- **活動管理**: 活動創建、更新、票種管理

## 🏗️ 技術架構

### 後端技術棧
- **FastAPI**: 現代 Python Web 框架
- **SQLAlchemy**: ORM 資料庫操作
- **PostgreSQL**: 主要資料庫
- **Alembic**: 資料庫遷移管理
- **Pydantic**: 資料驗證和序列化

### 資料庫設計
```
📊 核心資料表:
├── events (活動)
├── ticket_types (票種)
├── tickets (票券)
├── staff (員工)
├── staff_events (員工-活動權限)
└── checkin_logs (簽到記錄)
```

### API 設計
```
🌐 API 端點:
├── /api/staff/* (員工認證與管理)
├── /api/tickets/* (票券管理)
├── /api/checkin/* (簽到功能)
├── /api/events/* (活動管理)
└── /admin/api/* (管理端 API)
```

## 🚀 部署與運行

### 1. 環境準備
```bash
# 克隆專案
git clone <repository>
cd qr-checkin-system

# 創建虛擬環境
python -m venv myenv
source myenv/bin/activate  # macOS/Linux
# myenv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置文件設置
```bash
# 複製配置模板並填入實際值
cp alembic.ini.template alembic.ini
cp .env.template .env

# 編輯 alembic.ini 設置資料庫連接
# 將 postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME
# 替換為實際的資料庫連接資訊

# 編輯 .env 設置環境變數
# 包含資料庫URL、API密鑰等敏感資訊
```

### 2. 資料庫設置
```bash
# 啟動 PostgreSQL (使用 Docker)
docker-compose up -d

# 執行資料庫遷移
alembic upgrade head

# 創建測試資料
python create_test_data.py
```

### 3. 啟動服務
```bash
# 啟動 API 服務
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API 文檔: http://localhost:8000/docs
# 健康檢查: http://localhost:8000/health
```

## 🧪 測試

### 功能測試
```bash
# 完整功能測試
python test_complete_system.py

# 簡化認證測試
python test_simple_auth.py
```

### 測試賬號
- **管理員**: 用戶名 `admin`, 密碼 `admin123`
- **掃描員**: 登入碼參見測試資料創建輸出

## 📡 API 使用說明

### 認證方式
所有需要認證的 API 都使用 Header 認證:
```http
X-API-Key: test-api-key
Staff-ID: 1
```

### 核心流程示例

#### 1. 員工驗證
```bash
curl -X POST "http://localhost:8000/api/staff/verify" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### 2. 獲取票券 QR Code
```bash
curl -X GET "http://localhost:8000/api/tickets/1/qrcode"
```

#### 3. 票券驗證
```bash
curl -X POST "http://localhost:8000/api/tickets/verify" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "eyJhbGci..."}'
```

#### 4. 執行簽到
```bash
curl -X POST "http://localhost:8000/api/checkin" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -H "Staff-ID: 1" \
  -d '{"qr_token": "eyJhbGci...", "event_id": 1}'
```

## 🔧 配置說明

### 環境變數
```bash
# 資料庫連接
DATABASE_URL=postgresql://qr_admin:qr_pass@localhost:5432/qr_system

# 認證設定
API_KEY=test-api-key
SECRET_KEY=your-secret-key-change-in-production

# QR Code 設定
QR_TOKEN_EXPIRE_HOURS=168  # 7天過期
```

## 🎯 主要特色

### 1. 平台無關性
- RESTful API 設計，支援任何前端技術
- 標準 HTTP 介面，易於整合

### 2. 離線支援
- 票券資料預下載
- 離線簽到記錄緩存
- 網路恢復後自動同步

### 3. 安全機制
- JWT Token 防偽造
- API Key 認證
- 權限分級管理
- IP 和設備資訊記錄

### 4. 擴展性
- 模組化服務層設計
- 清晰的資料庫架構
- 支援水平擴展

## 📈 效能指標

### 測試結果
- ✅ 員工認證系統: 正常
- ✅ QR Code 生成與驗證: 正常
- ✅ 票券簽到功能: 正常
- ✅ 簽到記錄管理: 正常
- ✅ 離線同步功能: 正常
- ✅ 批次票券創建: 正常
- ✅ 權限控制系統: 正常
- ✅ 資料導出功能: 正常

## 🔮 未來擴展

### 可能的功能增強
1. **前端介面**: React/Vue.js 管理介面
2. **行動應用**: iOS/Android 掃描 App
3. **即時通知**: WebSocket 即時更新
4. **進階報表**: 更詳細的統計分析
5. **多語言支援**: 國際化功能
6. **API 版本控制**: v2 API 設計

## 📞 技術支援

- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/health
- **測試腳本**: `test_simple_auth.py`

---

**QR Check-in System v1.0.0** - 完整的票券簽到解決方案 🎉
