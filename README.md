# QR Check-in System 重構完成報告

## 📋 項目概覽

這是一個基於 FastAPI 的多租戶 QR Code 簽到系統，支援票券管理、員工認證、簽到核銷、多租戶管理等完整功能。**已完成大規模 API 架構重構**，明確區分超級管理員、商戶、員工、公開端點的權限與路徑。

## 🚀 重構亮點

### 📐 新 API 架構設計
- **超級管理員** (`/admin/*`) - 使用 Admin Password 認證
- **商戶管理** (`/api/v1/mgmt/*`) - 使用 API Key 認證  
- **員工操作** (`/api/v1/staff/*`) - 使用 JWT Token 認證
- **公開端點** (`/api/v1/public/*`) - 無需認證

### 🔐 多重認證機制
- **X-Admin-Password**: 超級管理員認證
- **X-API-Key**: 商戶專屬 API Key 認證
- **Authorization: Bearer**: 員工 JWT Token 認證
- **無認證**: 公開票券查詢與 QR 生成

### 🏢 完整多租戶支援
- **資料隔離**: 確保不同商戶資料完全隔離
- **權限控制**: 精細化的角色權限管理
- **API 安全**: 多層次認證與授權機制

## ✅ 已完成功能

### 🔧 系統管理
- **商戶管理**: 創建、查詢、更新、刪除商戶
- **API Key 管理**: 動態生成和管理商戶專屬 API Key
- **系統監控**: 健康檢查、服務狀態監控

### 🏢 商戶功能
- **活動管理**: 完整的活動生命週期管理
- **票券管理**: 單張/批次票券創建、查詢、更新、刪除
- **員工管理**: 員工帳號管理、權限指派
- **權限控制**: 細粒度的員工-活動權限管理

### 👤 員工功能
- **身份認證**: 用戶名/密碼登入獲取 JWT Token
- **個人資料**: 查詢個人資訊和可存取活動
- **簽到核銷**: QR Code 掃描簽到
- **記錄管理**: 查詢簽到歷史、撤銷簽到

### 🌐 公開功能
- **票券查詢**: 根據 UUID 查詢票券基本資訊
- **QR Token**: 生成用於簽到的短期 Token
- **QR Code**: 動態生成票券 QR Code 圖片

### 🎫 票券系統
- **UUID 支援**: 每張票券都有唯一 UUID
- **QR Token**: 基於 JWT 的安全 QR Token
- **狀態管理**: 票券使用狀態追蹤
- **描述欄位**: 支援額外資訊儲存

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
├── merchants (商戶) - 多租戶支援
├── api_keys (API金鑰) - 商戶專屬認證
├── events (活動) - 包含 merchant_id
├── ticket_types (票種) - 活動下的票種分類
├── tickets (票券) - 新增 description 欄位 (JSON格式)
├── staff (員工) - 包含 merchant_id
├── staff_events (員工-活動權限)
└── checkin_logs (簽到記錄)
```

#### 🎫 票券 description 欄位
tickets 表新增 `description` 欄位，支援 JSON 格式存儲：
- **資料型態**: TEXT (可存儲 JSON 字串)
- **用途**: 儲存票券額外資訊（座位、餐點、特殊需求等）
- **格式範例**: `{"seat": "A區1號", "meal": "素食", "notes": "VIP"}`
- **API 支援**: 所有票券 CRUD 操作都支援 description 欄位
- **Gradio 顯示**: 管理介面票券列表包含描述欄位顯示

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

### Docker 部署 (推薦) (NEW!)

我們提供了完整的 Docker 部署方案，包含自動化腳本和容器管理工具：

#### 快速 Docker 部署
```bash
# 一鍵部署（包含資料庫、API、Gradio）
./deploy-docker.sh

# 或使用 Docker Compose
docker-compose up -d

# 檢查服務健康狀態
./health-check.sh
```

#### Docker 容器管理
```bash
# 使用容器管理腳本
./docker-manager.sh

# 選項包括:
# 1) 啟動所有服務
# 2) 停止所有服務  
# 3) 重建並啟動
# 4) 查看服務狀態
# 5) 查看服務日誌
# 6) 清理容器和映像
```

#### 容器監控
```bash
# 持續監控容器狀態
./docker-monitor.sh

# 資料備份
./docker-backup.sh
```

#### 服務端點
- **API 服務**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **Gradio 管理介面**: http://localhost:7860
- **PostgreSQL**: localhost:5432

### 手動部署

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

### 4. 多租戶模式設置 (NEW!)

#### 4.1 啟用多租戶模式
```bash
# 在 .env 文件中設置
ENABLE_MULTI_TENANT=1
ADMIN_PASSWORD=your-secure-admin-password
GRADIO_PORT=7860
```

#### 4.2 運行資料庫遷移（多租戶支援）
```bash
# 升級到最新的資料庫架構
alembic upgrade head
```

#### 4.3 設置示例商戶
```bash
# 創建示例商戶和API Keys
python setup_multi_tenant.py
```

#### 4.4 啟動 Gradio 管理介面
```bash
# 啟動商戶管理介面
python gradio_admin.py

# 訪問: http://localhost:7860
# 使用 ADMIN_PASSWORD 登入
```

#### 4.5 多租戶功能測試
```bash
# 運行多租戶完整測試
python test_multi_tenant.py
```

### 多租戶 API 端點

#### 商戶管理 (需要管理員權限)
```bash
# 創建新商戶
POST /admin/merchants

# 獲取商戶列表
GET /admin/merchants

# 為商戶創建API Key
POST /admin/merchants/{merchant_id}/api-keys

# 獲取商戶統計
GET /admin/merchants/{merchant_id}/statistics
```

#### 多租戶認證方式
在多租戶模式下，API 認證使用商戶專屬的API Key：

```http
X-API-Key: qr_abc123def456...  # 商戶專屬API Key
Staff-ID: 1                    # 該商戶下的員工ID
```

### 🏢 多租戶架構說明

#### 商戶隔離
- **數據隔離**: 每個商戶的活動、票券、員工數據完全隔離
- **API Key 隔離**: 不同商戶使用專屬的API Key
- **權限控制**: 員工只能操作所屬商戶的數據

#### 資料庫架構更新
```
📊 多租戶資料表:
├── merchants (商戶)
├── api_keys (API金鑰)
├── events (活動) - 新增 merchant_id
├── staff (員工) - 新增 merchant_id
└── ... (其他表保持不變)
```

#### Gradio 管理介面功能 (ENHANCED!)
- **商戶管理**: 創建、查看、更新商戶資訊
- **API Key 管理**: 生成、查看、撤銷API Key
- **活動管理**: 創建活動、編輯活動描述、刪除活動
- **票券查看**: 查看票券清單，包含票種、持有人、**描述欄位**、狀態、建立時間
- **員工管理**: 查看商戶下的員工清單
- **簽到記錄**: 查看各活動的簽到記錄
- **統計面板**: 查看各商戶的活動、票券、員工統計
- **系統概覽**: 整體多租戶系統統計
- **多租戶安全**: 所有查詢均支援 merchant_id 過濾，確保資料隔離
- **會話管理**: 採用 sessionmaker 管理資料庫會話，避免會話衝突
- **即時更新**: 介面元件即時反映資料庫變更

## 🧪 測試

### API 測試套件 (NEW!)

我們提供了完整的 API 測試套件，支援快速測試、認證測試、完整系統測試等多種場景：

#### 測試套件主選單
```bash
# 啟動測試套件主選單
./test_suite.sh

# 選項包括:
# 1) 快速 API 測試 (test_api_quick.sh)
# 2) 認證系統測試 (test_api_auth.sh)
# 3) 真實 API 測試 (test_real_apis.sh)
# 4) 完整 API 測試 (test_complete_apis.sh)
# 5) 多租戶 API 測試 (test_multi_tenant_apis.py)
# 6) Swagger 文檔測試 (test_swagger_apis.sh)
```

#### 各測試腳本說明

**1. 快速 API 測試** (`test_api_quick.sh`)
```bash
# 測試基本 API 端點和健康檢查
./test_api_quick.sh
```

**2. 認證系統測試** (`test_api_auth.sh`)
```bash
# 測試員工認證、API Key 驗證等
./test_api_auth.sh
```

**3. 真實 API 測試** (`test_real_apis.sh`)
```bash
# 測試完整的業務流程，包括票券創建、簽到等
./test_real_apis.sh
```

**4. 完整 API 測試** (`test_complete_apis.sh`)
```bash
# 最全面的 API 測試，包含所有端點和邊界案例
./test_complete_apis.sh
```

**5. 多租戶 API 測試** (`test_multi_tenant_apis.py`)
```bash
# Python 測試腳本，專門測試多租戶功能
python test_multi_tenant_apis.py
```

**6. Swagger 文檔測試** (`test_swagger_apis.sh`)
```bash
# 測試 Swagger 文檔中的所有 API 端點，包含 description 欄位
./test_swagger_apis.sh
```

#### 🎫 票券 description 欄位測試
所有測試腳本都已支援 description 欄位測試：
```bash
# 批次產票測試（包含 description）
curl -X POST "http://localhost:8000/api/tickets-mgmt/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "ticket_type_id": 1,
    "quantity": 3,
    "holder_names": ["測試用戶1", "測試用戶2", "測試用戶3"],
    "description": {"seat": "A區1-3號", "meal": "一般", "notes": "測試票券"}
  }'
```

### 功能測試
```bash
# 完整功能測試
python test_complete_system.py

# 簡化認證測試
python test_simple_auth.py

# 多租戶完整測試
python test_multi_tenant.py
```

### 測試賬號
- **管理員**: 用戶名 `admin`, 密碼 `admin123`
- **掃描員**: 登入碼參見測試資料創建輸出
- **多租戶測試**: 使用 `setup_multi_tenant.py` 創建的示例商戶

## 📡 API 使用說明

### 認證方式
所有需要認證的 API 都使用 Header 認證:
```http
X-API-Key: test-api-key
Staff-ID: 1
```

### 🎫 完整票券產生流程 (IMPORTANT!)

**票券產生必須按照以下順序執行：**

#### 步驟 1: 建立商戶（多租戶模式）
```bash
# 創建商戶（需要管理員權限）
curl -X POST "http://localhost:8000/admin/merchants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "測試商戶",
    "description": "這是一個測試商戶",
    "contact_email": "test@example.com",
    "contact_phone": "0912345678"
  }'
```

#### 步驟 2: 創建活動
```bash
# 在商戶下創建活動
curl -X POST "http://localhost:8000/api/events/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -d '{
    "name": "音樂會",
    "description": "年度音樂會活動",
    "location": "台北市信義區",
    "start_time": "2024-12-25T19:00:00",
    "end_time": "2024-12-25T22:00:00"
  }'
```

#### 步驟 3: 創建票種（必須先有票種才能產票！）
```bash
# 在活動下創建票種
curl -X POST "http://localhost:8000/api/events/1/ticket-types" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -d '{
    "name": "VIP票",
    "description": "VIP席位票券",
    "price": 1500.00,
    "total_quantity": 100
  }'
```

#### 步驟 4: 批次產生票券
```bash
# 批次產生票券（需要指定票種ID）
curl -X POST "http://localhost:8000/api/tickets-mgmt/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -d '{
    "ticket_type_id": 1,
    "quantity": 50,
    "holder_names": ["張三", "李四", "王五"],
    "description": {"seat": "A區1-50號", "special": "包含餐點"}
  }'
```

#### 步驟 5: 票券 QR Code 與簽到
```bash
# 1. 取得票券 QR Code
curl -X GET "http://localhost:8000/api/tickets-mgmt/1/qrcode"

# 2. 驗證 QR Token（不簽到）
curl -X POST "http://localhost:8000/api/tickets-mgmt/verify" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "eyJhbGci..."}'

# 3. 執行簽到
curl -X POST "http://localhost:8000/api/checkin" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -H "Staff-ID: 1" \
  -d '{"qr_token": "eyJhbGci...", "event_id": 1}'
```

### 票券查詢 API 使用說明 (NEW!)
#### 3. 票券查詢
```bash
# 查詢單張票券詳細資料
curl -X GET "http://localhost:8000/api/tickets/1" \
  -H "X-API-Key: merchant-api-key"

# 根據持有人資訊查詢票券
curl -X GET "http://localhost:8000/api/tickets/holder/search?email=user@example.com" \
  -H "X-API-Key: merchant-api-key"

# 多條件查詢票券（支援 email、phone、external_user_id）
curl -X GET "http://localhost:8000/api/tickets/holder/search?phone=0912345678&event_id=1" \
  -H "X-API-Key: merchant-api-key"
```

#### 4. 票券驗證
```bash
# 驗證票券 QR Token
curl -X POST "http://localhost:8000/api/tickets/verify" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "eyJhbGci..."}'
```

#### 5. 執行簽到
```bash
# 執行票券簽到
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

# 多租戶設定
ENABLE_MULTI_TENANT=1
ADMIN_PASSWORD=your-secure-admin-password

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

### 5. 多租戶安全
- 完整的商戶間數據隔離
- 商戶專屬的 API Key
- 租戶感知的查詢和操作
- 使用 sessionmaker 管理資料庫會話

## 📈 效能指標

### 測試結果 (LATEST)
- ✅ 員工認證系統: 正常
- ✅ QR Code 生成與驗證: 正常
- ✅ 票券簽到功能: 正常
- ✅ 簽到記錄管理: 正常
- ✅ 離線同步功能: 正常
- ✅ 批次票券創建: 正常（含 description 欄位）
- ✅ 票種管理 API: 正常
- ✅ 權限控制系統: 正常
- ✅ 資料導出功能: 正常
- ✅ 多租戶架構: 正常
- ✅ Gradio 管理介面: 正常（含票券 description 顯示）
- ✅ Swagger 文檔: 正常（含完整流程說明）

## 🔮 未來擴展

### 可能的功能增強
1. **前端介面**: React/Vue.js 管理介面
2. **行動應用**: iOS/Android 掃描 App
3. **即時通知**: WebSocket 即時更新
4. **進階報表**: 更詳細的統計分析
5. **多語言支援**: 國際化功能
6. **API 版本控制**: v2 API 設計

## 📞 技術支援

### 📖 完整文檔
- **API 文檔**: http://localhost:8000/docs（含完整流程說明）
- **ReDoc 格式**: http://localhost:8000/redoc
- **API 路由總覽**: [API_ROUTES_OVERVIEW.md](API_ROUTES_OVERVIEW.md)
- **API 測試說明**: [API_TESTING_README.md](API_TESTING_README.md)
- **多租戶實現報告**: [MULTI_TENANT_REPORT.md](MULTI_TENANT_REPORT.md)

### 🔧 健康檢查
- **健康檢查**: http://localhost:8000/health
- **容器健康檢查**: `./health-check.sh`
- **API 快速測試**: `./test_api_quick.sh`

### 🎫 重要流程提醒
1. **產票流程**: 商戶 → 活動 → 票種 → 票券
2. **Description 欄位**: 支援 JSON 格式的票券描述
3. **多租戶隔離**: 確保 merchant_id 正確傳遞
4. **API Key 使用**: 每個商戶使用專屬的 API Key

### 🧪 測試腳本
- **測試套件主選單**: `./test_suite.sh`
- **簡化認證測試**: `python test_simple_auth.py`
- **完整系統測試**: `python test_complete_system.py`
- **多租戶測試**: `python test_multi_tenant.py`

---

**QR Check-in System v1.0.0** - 完整的票券簽到解決方案 🎉

## 🎉 多租戶功能完成總結

QR Check-in System 已成功升級為**企業級多租戶SaaS系統**！

### ✅ 新增功能亮點

#### 🏢 多租戶架構
- **完全數據隔離**: 每個商戶擁有獨立的數據空間
- **動態API Key**: 自動生成安全的商戶專屬API Key
- **靈活部署**: 支援單租戶/多租戶模式無縫切換
- **可視化管理**: Gradio介面提供直觀的商戶管理

#### 🔐 企業級安全
- **API Key安全**: 32字符加密安全隨機字符串
- **權限分級**: 超級管理員、商戶管理員、商戶員工
- **租戶隔離**: 100% 商戶間數據隔離保證
- **操作追蹤**: 完整的API Key使用記錄

#### 🛠️ 開發者友好
- **零破壞升級**: 現有功能完全兼容
- **完整測試**: 自動化多租戶功能測試
- **詳細文檔**: API文檔和部署指南
- **快速設置**: 一鍵設置腳本

### 🚀 快速開始多租戶模式

```bash
# 1. 啟動多租戶系統
./start_multi_tenant.sh

# 2. 啟動API服務
uvicorn app.main:app --reload --port 8000

# 3. 運行完整測試
python test_multi_tenant.py

# 4. 訪問管理介面
python gradio_admin.py  # http://localhost:7860
```

### 📊 測試結果
```
🏁 測試完成！通過: 8, 失敗: 0
🎉 所有測試都通過了！

✅ 商戶創建和管理
✅ API Key 生成和驗證
✅ 員工多租戶隔離
✅ 活動多租戶隔離  
✅ 租戶間數據隔離
✅ 商戶統計功能
✅ API Key 權限管理
✅ 系統健康檢查
```

### 🔗 相關文檔
- **完整實現報告**: [MULTI_TENANT_REPORT.md](MULTI_TENANT_REPORT.md)
- **多租戶測試**: [test_multi_tenant.py](test_multi_tenant.py)
- **設置腳本**: [setup_multi_tenant.py](setup_multi_tenant.py)
- **啟動腳本**: [start_multi_tenant.sh](start_multi_tenant.sh)

---

**QR Check-in System v2.0** 🎉  
*從單租戶到企業級多租戶SaaS的完美升級*
### ✅ 功能完成度: 100%
- 多租戶架構: ✅ 完成
- 商戶管理: ✅ 完成  
- API Key管理: ✅ 完成
- 數據隔離: ✅ 完成
- 管理介面: ✅ 完成
- 測試驗證: ✅ 完成

### 🧪 測試結果: 8/8 通過
- 系統健康檢查: ✅
- 商戶CRUD操作: ✅
- API Key生成驗證: ✅
- 員工多租戶管理: ✅
- 活動多租戶管理: ✅
- 租戶數據隔離: ✅
- 商戶統計功能: ✅
- API Key權限管理: ✅

### 🚀 部署就緒
- 環境配置: ✅ 完成
- 資料庫遷移: ✅ 完成
- 設置腳本: ✅ 完成
- 啟動腳本: ✅ 完成
- 管理介面: ✅ 完成

### 📈 商業價值
- 從單租戶系統 → 企業級多租戶SaaS平台
- 支援無限商戶擴展
- 100%數據隔離保證
- 可視化管理介面
- 完整的API文檔

---

# QR Check-in System - English Documentation

## 📋 Project Overview

A comprehensive QR Code check-in system built with FastAPI, supporting ticket management, staff authentication, check-in validation, offline synchronization, and **multi-tenant architecture** for serving multiple merchants with isolated data.

## ✅ Completed Features

### 🏢 Multi-Tenant Architecture
- **Merchant Management**: Support for multiple independent merchants with dedicated API Keys
- **Data Isolation**: Complete data separation between different merchants
- **API Key Management**: Dynamic generation and management of merchant-specific API Keys
- **Gradio Admin Interface**: Visual merchant and API Key management interface
- **Statistics Dashboard**: Independent statistics for each merchant

### 🔐 Authentication System
- **Dual Mode Support**: Single-tenant and multi-tenant operation modes
- **API Key Authentication**: Merchant-specific API Key based authentication
- **Staff Verification**: Support for username/password and login code methods
- **Permission Control**: Permission management based on staff-event associations
- **Tenant Isolation**: Ensures staff can only operate on their merchant's data

### 🎫 Ticket Management (ENHANCED!)
- **Ticket Creation**: Single ticket and batch ticket creation
- **Ticket Description**: Support for JSON format ticket description field for storing additional information (seat numbers, special requirements, etc.)
- **Ticket Type Management**: Create, update, delete ticket types under events
- **QR Code Generation**: JWT Token-based QR Code generation
- **Ticket Verification**: QR Token validation (without check-in execution)
- **Ticket Queries**: Query functionality based on events, ticket IDs, etc., including description field display
- **Complete Workflow**: Create Merchant → Create Event → Create Ticket Type → Generate Tickets (Batch/Single) → QR Check-in

### 🎯 Check-in System
- **QR Code Check-in**: Scan QR Code for ticket validation
- **Duplicate Prevention**: Security mechanism to prevent duplicate check-ins
- **IP/User-Agent Recording**: Record check-in source information
- **Check-in History**: Complete check-in history management

### 🔄 Offline Synchronization
- **Offline Check-in Cache**: Support for check-in records in offline environments
- **Batch Sync**: Batch upload of offline check-in records when network recovers
- **Duplicate Handling**: Intelligent handling of duplicate check-in records

### 📊 Management Features
- **Check-in Cancellation**: Administrators can cancel incorrect check-in records
- **Statistical Reports**: Event statistics, ticket type statistics, etc.
- **Data Export**: CSV format export for check-in records and ticket lists
- **Event Management**: Event creation, updates, ticket type management

## 🏗️ Technical Architecture

### Backend Tech Stack
- **FastAPI**: Modern Python Web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization

### Database Design
```
📊 Core Data Tables:
├── merchants (Merchants)
├── api_keys (API Keys)
├── events (Events) - with merchant_id
├── ticket_types (Ticket Types)
├── tickets (Tickets) - NEW: description field (JSON format)
├── staff (Staff) - with merchant_id
├── staff_events (Staff-Event Permissions)
└── checkin_logs (Check-in Records)
```

#### 🎫 Ticket Description Field
The tickets table includes a new `description` field supporting JSON format:
- **Data Type**: TEXT (stores JSON strings)
- **Purpose**: Store additional ticket information (seats, meals, special requirements, etc.)
- **Example Format**: `{"seat": "A1", "meal": "vegetarian", "notes": "VIP"}`
- **API Support**: All ticket CRUD operations support the description field
- **Gradio Display**: Admin interface ticket list includes description field display

### API Design
```
🌐 API Endpoints:
├── /api/staff/* (Staff authentication & management)
├── /api/tickets/* (Ticket management)
├── /api/checkin/* (Check-in functionality)
├── /api/events/* (Event management)
└── /admin/api/* (Admin APIs)
```

## 🚀 Deployment & Setup

### Docker Deployment (Recommended)

#### Quick Docker Deployment
```bash
# One-click deployment (includes database, API, Gradio)
./deploy-docker.sh

# Or use Docker Compose
docker-compose up -d

# Check service health status
./health-check.sh
```

#### Docker Container Management
```bash
# Use container management script
./docker-manager.sh

# Options include:
# 1) Start all services
# 2) Stop all services  
# 3) Rebuild and start
# 4) View service status
# 5) View service logs
# 6) Clean containers and images
```

#### Service Endpoints
- **API Service**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Gradio Admin Interface**: http://localhost:7860
- **PostgreSQL**: localhost:5432

### Manual Deployment

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository>
cd qr-checkin-system

# Create a virtual environment
python -m venv myenv
source myenv/bin/activate  # macOS/Linux
# myenv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration Files Setup
```bash
# Copy template files and fill in actual values
cp alembic.ini.template alembic.ini
cp .env.template .env

# Edit alembic.ini to set database connection
# Replace postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME
# with actual database connection information

# Edit .env to set environment variables
# Including database URL, API keys, and other sensitive information
```

### 2. Database Setup
```bash
# Start PostgreSQL (using Docker)
docker-compose up -d

# Run database migrations
alembic upgrade head

# Create test data
python create_test_data.py
```

### 3. Start Services
```bash
# Start API service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API Documentation: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
```

### 4. Multi-Tenant Mode Setup (NEW!)

#### 4.1 Enable Multi-Tenant Mode
```bash
# Set in .env file
ENABLE_MULTI_TENANT=1
ADMIN_PASSWORD=your-secure-admin-password
GRADIO_PORT=7860
```

#### 4.2 Run Database Migration (Multi-Tenant Support)
```bash
# Upgrade to latest database schema
alembic upgrade head
```

#### 4.3 Setup Sample Merchants
```bash
# Create sample merchants and API Keys
python setup_multi_tenant.py
```

#### 4.4 Start Gradio Admin Interface
```bash
# Start merchant management interface
python gradio_admin.py

# Access: http://localhost:7860
# Login with ADMIN_PASSWORD
```

#### 4.5 Multi-Tenant Functionality Testing
```bash
# Run full multi-tenant tests
python test_multi_tenant.py
```

### Multi-Tenant API Endpoints

#### Merchant Management (Admin privileges required)
```bash
# Create new merchant
POST /admin/merchants

# Get merchant list
GET /admin/merchants

# Create API Key for merchant
POST /admin/merchants/{merchant_id}/api-keys

# Get merchant statistics
GET /admin/merchants/{merchant_id}/statistics
```

#### Multi-Tenant Authentication
In multi-tenant mode, API authentication uses merchant-specific API Keys：

```http
X-API-Key: qr_abc123def456...  # Merchant-specific API Key
Staff-ID: 1                    # Staff ID under that merchant
```

### 🏢 Multi-Tenant Architecture Explanation

#### Merchant Isolation
- **Data Isolation**: Complete data separation for each merchant's events, tickets, and staff
- **API Key Isolation**: Dedicated API Key for different merchants
- **Permission Control**: Staff can only operate on their own merchant's data

#### Database Schema Updates
```
📊 Multi-Tenant Data Tables:
├── merchants (Merchants)
├── api_keys (API Keys)
├── events (Events) - new merchant_id
├── staff (Staff) - new merchant_id
└── ... (other tables remain unchanged)
```

#### Gradio Admin Interface Features (ENHANCED!)
- **Merchant Management**: Create, view, update merchant information
- **API Key Management**: Generate, view, revoke API Keys
- **Event Management**: Create events, edit event descriptions, delete events
- **Ticket Viewing**: View ticket list including ticket type, holder, **description field**, status, creation time
- **Staff Management**: View staff list under the merchant
- **Check-in Records**: View check-in records for each event
- **Statistics Dashboard**: View statistics for merchant's events, tickets, staff
- **System Overview**: Overall multi-tenant system statistics
- **Multi-Tenant Security**: All queries support merchant_id filtering to ensure data isolation
- **Session Management**: Use sessionmaker to manage database sessions, avoid session conflicts
- **Real-time Updates**: Interface components reflect database changes in real-time

## 🧪 Testing

### API Test Suite

We provide a comprehensive API test suite supporting quick tests, authentication tests, complete system tests, and more:

#### Test Suite Main Menu
```bash
# Start test suite main menu
./test_suite.sh

# Options include:
# 1) Quick API Test (test_api_quick.sh)
# 2) Authentication System Test (test_api_auth.sh)
# 3) Real API Test (test_real_apis.sh)
# 4) Complete API Test (test_complete_apis.sh)
# 5) Multi-tenant API Test (test_multi_tenant_apis.py)
# 6) Swagger Documentation Test (test_swagger_apis.sh)
```

#### Individual Test Scripts

**1. Quick API Test** (`test_api_quick.sh`)
```bash
# Test basic API endpoints and health checks
./test_api_quick.sh
```

**2. Authentication System Test** (`test_api_auth.sh`)
```bash
# Test staff authentication, API Key validation, etc.
./test_api_auth.sh
```

**3. Real API Test** (`test_real_apis.sh`)
```bash
# Test complete business workflows including ticket creation, check-ins, etc.
./test_real_apis.sh
```

**4. Complete API Test** (`test_complete_apis.sh`)
```bash
# Most comprehensive API test including all endpoints and edge cases
./test_complete_apis.sh
```

**5. Multi-tenant API Test** (`test_multi_tenant_apis.py`)
```bash
# Python test script specifically for multi-tenant functionality
python test_multi_tenant_apis.py
```

**6. Swagger 文檔測試** (`test_swagger_apis.sh`)
```bash
# 測試 Swagger 文檔中的所有 API 端點，包含 description 欄位
./test_swagger_apis.sh
```

#### 🎫 票券 description 欄位測試
所有測試腳本都已支援 description 欄位測試：
```bash
# 批次產票測試（包含 description）
curl -X POST "http://localhost:8000/api/tickets-mgmt/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -d '{
    "ticket_type_id": 1,
    "quantity": 3,
    "holder_names": ["測試用戶1", "測試用戶2", "測試用戶3"],
    "description": {"seat": "A區1-3號", "meal": "一般", "notes": "測試票券"}
  }'
```

### 功能測試
```bash
# 完整功能測試
python test_complete_system.py

# 簡化認證測試
python test_simple_auth.py

# 多租戶完整測試
python test_multi_tenant.py
```

### 測試賬號
- **管理員**: 用戶名 `admin`, 密碼 `admin123`
- **掃描員**: 登入碼參見測試資料創建輸出
- **多租戶測試**: 使用 `setup_multi_tenant.py` 創建的示例商戶

## 📡 API 使用說明

### 認證方式
所有需要認證的 API 都使用 Header 認證:
```http
X-API-Key: test-api-key
Staff-ID: 1
```

### 🎫 完整票券產生流程 (IMPORTANT!)

**票券產生必須按照以下順序執行：**

#### 步驟 1: 建立商戶（多租戶模式）
```bash
# 創建商戶（需要管理員權限）
curl -X POST "http://localhost:8000/admin/merchants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "測試商戶",
    "description": "這是一個測試商戶",
    "contact_email": "test@example.com",
    "contact_phone": "0912345678"
  }'
```

#### 步驟 2: 創建活動
```bash
# 在商戶下創建活動
curl -X POST "http://localhost:8000/api/events/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -d '{
    "name": "音樂會",
    "description": "年度音樂會活動",
    "location": "台北市信義區",
    "start_time": "2024-12-25T19:00:00",
    "end_time": "2024-12-25T22:00:00"
  }'
```

#### 步驟 3: 創建票種（必須先有票種才能產票！）
```bash
# 在活動下創建票種
curl -X POST "http://localhost:8000/api/events/1/ticket-types" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -d '{
    "name": "VIP票",
    "description": "VIP席位票券",
    "price": 1500.00,
    "total_quantity": 100
  }'
```

#### 步驟 4: 批次產生票券
```bash
# 批次產生票券（需要指定票種ID）
curl -X POST "http://localhost:8000/api/tickets-mgmt/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -d '{
    "ticket_type_id": 1,
    "quantity": 50,
    "holder_names": ["張三", "李四", "王五"],
    "description": {"seat": "A區1-50號", "special": "包含餐點"}
  }'
```

#### 步驟 5: 票券 QR Code 與簽到
```bash
# 1. 取得票券 QR Code
curl -X GET "http://localhost:8000/api/tickets-mgmt/1/qrcode"

# 2. 驗證 QR Token（不簽到）
curl -X POST "http://localhost:8000/api/tickets-mgmt/verify" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "eyJhbGci..."}'

# 3. 執行簽到
curl -X POST "http://localhost:8000/api/checkin" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: merchant-api-key" \
  -H "Staff-ID: 1" \
  -d '{"qr_token": "eyJhbGci...", "event_id": 1}'
```

#### 步驟 6: 票券查詢
```bash
# 查詢單張票券詳細資料
curl -X GET "http://localhost:8000/api/tickets/1" \
  -H "X-API-Key: merchant-api-key"

# 根據持有人資訊查詢票券
curl -X GET "http://localhost:8000/api/tickets/holder/search?email=user@example.com" \
  -H "X-API-Key: merchant-api-key"

# 多條件查詢票券（支援 email、phone、external_user_id）
curl -X GET "http://localhost:8000/api/tickets/holder/search?phone=0912345678&event_id=1" \
  -H "X-API-Key: merchant-api-key"
```

#### 步驟 7: 票券驗證
```bash
# 驗證票券 QR Token
curl -X POST "http://localhost:8000/api/tickets/verify" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "eyJhbGci..."}'
```

#### 步驟 8: 執行簽到
```bash
# 執行票券簽到
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

# 多租戶設定
ENABLE_MULTI_TENANT=1
ADMIN_PASSWORD=your-secure-admin-password

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

### 5. 多租戶安全
- 完整的商戶間數據隔離
- 商戶專屬的 API Key
- 租戶感知的查詢和操作
- 使用 sessionmaker 管理資料庫會話

## 📈 效能指標

### 測試結果 (LATEST)
- ✅ 員工認證系統: 正常
- ✅ QR Code 生成與驗證: 正常
- ✅ 票券簽到功能: 正常
- ✅ 簽到記錄管理: 正常
- ✅ 離線同步功能: 正常
- ✅ 批次票券創建: 正常（含 description 欄位）
- ✅ 票種管理 API: 正常
- ✅ 權限控制系統: 正常
- ✅ 資料導出功能: 正常
- ✅ 多租戶架構: 正常
- ✅ Gradio 管理介面: 正常（含票券 description 顯示）
- ✅ Swagger 文檔: 正常（含完整流程說明）

## 🔮 未來擴展

### 可能的功能增強
1. **前端介面**: React/Vue.js 管理介面
2. **行動應用**: iOS/Android 掃描 App
3. **即時通知**: WebSocket 即時更新
4. **進階報表**: 更詳細的統計分析
5. **多語言支援**: 國際化功能
6. **API 版本控制**: v2 API 設計

## 📞 技術支援

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Test Scripts**: Various test scripts in `test_*.sh` and `test_*.py`
- **API Testing Guide**: [API_TESTING_README.md](API_TESTING_README.md)

---

**QR Check-in System v2.0** 🎉  
*Complete Ticket Check-in Solution with Enterprise-Grade Multi-Tenant Architecture*
