# QR Check-in System 重構完成報告

## 📋 項目概覽

這是一個基於 FastAPI 的多租戶 QR Code 簽到系統，支援票券管理、員工認證、簽到核銷、多租戶管理等完整功能。**已完成大規模 API 架構重構**，明確區分超級管理員、商戶、員工、公開端點的權限與路徑。

## 🚀 重構亮點

### 📐 新 API 架構設計
- **超級管理員** (`/admin/*`) - 使用 Admin Password 認證
- **商戶管理** (`/api/v1/mgmt/*`) - 使用 API Key 認證  
- **員工操作** (`/api/v1/staff/*`) - 使用 JWT Token 認證
-

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

#### 🕐 員工活動列表時間過濾 (NEW!)
員工查詢可存取活動 (`GET /api/v1/staff/me/events`) 採用智能時間過濾機制：

**過濾規則：**
- **活動開始時間**: 今天到未來30天內的活動
- **活動結束時間**: 不早於昨天（活動結束後1天內仍可見）
- **排序方式**: 依活動開始時間升序排列

**設計理念：**
- 避免顯示過多歷史活動，提升用戶體驗
- 保留彈性時間：方便會前準備和事後統計
- 商戶可能有數百個活動，時間過濾確保介面簡潔實用

**權限說明：**
- 若員工有特定活動權限設定，則依據設定
- 若無特定設定，預設為可簽到但不可撤銷

### 🌐 公開功能
- **票券查詢**: 根據 UUID 查詢票券基本資訊
- **QR Token**: 生成用於簽到的短期 Token
- **QR Code**: 動態生成票券 QR Code 圖片
- **會員票券查詢頁面**: 友善的網頁介面供持票人查詢票券資訊

### 🎫 票券系統
- **UUID 支援**: 每張票券都有唯一 UUID
- **QR Token**: 基於 JWT 的安全 QR Token
- **狀態管理**: 票券使用狀態追蹤
- **描述欄位**: 支援額外資訊儲存
- **靜態網頁**: 提供美觀的會員查詢介面

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
- **會員票券查詢**: http://localhost:8000/member-ticket
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

## 🎫 會員票券查詢功能

系統提供了一個美觀友善的網頁介面，讓持票人可以輕鬆查詢自己的票券資訊。

### 🌐 訪問方式
訪問 **`http://your-domain:8000/member-ticket`** 來使用會員票券查詢功能。

### ✨ 功能特色
- **直觀操作**: 只需輸入票券 UUID 即可查詢
- **詳細資訊**: 顯示活動資訊、票券狀態、持票人資訊
- **QR Code 顯示**: 自動顯示入場用 QR Code（未使用票券）
- **響應式設計**: 支援手機、平板、桌面設備
- **即時狀態**: 即時顯示票券是否已使用

### 📱 使用流程
1. 打開會員票券查詢頁面
2. 輸入您的票券 UUID（可從購票確認郵件中獲得）
3. 點擊「查詢我的票券」按鈕
4. 查看票券詳細資訊和入場 QR Code
5. 向工作人員出示 QR Code 進行入場驗證

### 🎨 頁面功能
- **活動資訊**: 活動名稱、描述、地點、時間
- **票券狀態**: 有效/已使用狀態標示
- **持票人資訊**: 姓名、聯絡方式
- **QR Code**: 動態生成的入場憑證
- **錯誤處理**: 友善的錯誤提示訊息

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

## 🟢 離線簽到批次同步 API（2025/06 新增）

支援掃描員工於會場無網路時，將多筆簽到資料暫存，待網路恢復後一次上傳。

### API 路徑
POST `/api/v1/staff/checkin/sync`

### 認證
- 需員工 JWT（Authorization: Bearer ...）

### 請求格式
```json
{
  "event_id": 1,
  "checkins": [
    {
      "ticket_id": 101,
      "event_id": 1,
      "checkin_time": "2025-06-25T10:30:00.000000",
      "client_timestamp": "1720000000"
    },
    ...
  ]
}
```

### 回應格式
```json
{
  "success": true,
  "message": "同步成功，共新增 2 筆簽到紀錄。"
}
```

### curl 範例
```bash
curl -X POST "http://localhost:8000/api/v1/staff/checkin/sync" \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "checkins": [
      {"ticket_id": 101, "event_id": 1, "checkin_time": "2025-06-25T10:30:00.000000", "client_timestamp": "1720000000"},
      {"ticket_id": 102, "event_id": 1, "checkin_time": "2025-06-25T10:31:00.000000", "client_timestamp": "1720000060"}
    ]
  }'
```

### 注意事項
- 已簽到過的票券會自動跳過，不會重複簽到。
- 回傳訊息會顯示實際新增的簽到筆數。
- 請於網路恢復時盡快同步，避免資料遺失。

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
