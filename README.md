# QR Check-in System 完成報告

## 📋 項目概覽

這是一個基於 FastAPI 的綜合性 QR Code 簽到系統，支援票券管理、員工認證、簽到核銷、離線同步等完整功能。**現已支援多租戶架構**，可為多個商戶提供獨立的票券管理服務。

## ✅ 已完成功能

### 🏢 多租戶架構 (NEW!)
- **商戶管理**: 支援多個獨立商戶，每個商戶擁有專屬的API Key
- **數據隔離**: 確保不同商戶的數據完全隔離
- **API Key 管理**: 動態生成和管理商戶專屬的API Key
- **Gradio 管理介面**: 可視化的商戶和API Key管理介面
- **統計面板**: 為每個商戶提供獨立的統計數據

### 🔐 認證系統
- **雙模式支援**: 支援單租戶和多租戶兩種運行模式
- **API Key 認證**: 基於商戶專屬API Key的認證機制
- **員工驗證**: 支援用戶名/密碼和登入碼兩種方式
- **權限控制**: 基於員工-活動關聯的權限管理系統
- **租戶隔離**: 確保員工只能操作所屬商戶的數據

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
# 專門測試多租戶功能的 Python 測試腳本
python test_multi_tenant_apis.py
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

### 🎫 Ticket Management
- **Ticket Creation**: Single ticket and batch ticket creation
- **QR Code Generation**: JWT Token-based QR Code generation
- **Ticket Verification**: QR Token validation (without check-in execution)
- **Ticket Queries**: Query functionality based on events, ticket IDs, etc.

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
├── tickets (Tickets)
├── staff (Staff) - with merchant_id
├── staff_events (Staff-Event Permissions)
└── checkin_logs (Check-in Records)
```

### API Design
```
🌐 API Endpoints:
├── /api/staff/* (Staff authentication & management)
├── /api/tickets/* (Ticket management)
├── /api/checkin/* (Check-in functionality)
├── /api/events/* (Event management)
├── /admin/api/* (Admin APIs)
└── /admin/merchants/* (Multi-tenant merchant management)
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

### Multi-Tenant Mode Setup

#### Enable Multi-Tenant Mode
```bash
# Set in .env file
ENABLE_MULTI_TENANT=1
ADMIN_PASSWORD=your-secure-admin-password
GRADIO_PORT=7860
```

#### Run Database Migration (Multi-tenant Support)
```bash
# Upgrade to latest database schema
alembic upgrade head
```

#### Setup Sample Merchants
```bash
# Create sample merchants and API Keys
python setup_multi_tenant.py
```

#### Start Gradio Admin Interface
```bash
# Start merchant management interface
python gradio_admin.py

# Access: http://localhost:7860
# Login with ADMIN_PASSWORD
```

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
In multi-tenant mode, API authentication uses merchant-specific API Keys:

```http
X-API-Key: qr_abc123def456...  # Merchant-specific API Key
Staff-ID: 1                    # Staff ID under that merchant
```

## 📡 API Usage Guide

### Authentication Method
All APIs requiring authentication use Header authentication:
```http
X-API-Key: test-api-key
Staff-ID: 1
```

### Core Workflow Examples

#### 1. Staff Verification
```bash
curl -X POST "http://localhost:8000/api/staff/verify" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### 2. Get Ticket QR Code
```bash
curl -X GET "http://localhost:8000/api/tickets/1/qrcode"
```

#### 3. Ticket Verification
```bash
curl -X POST "http://localhost:8000/api/tickets/verify" \
  -H "Content-Type: application/json" \
  -d '{"qr_token": "eyJhbGci..."}'
```

#### 4. Execute Check-in
```bash
curl -X POST "http://localhost:8000/api/checkin" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key" \
  -H "Staff-ID: 1" \
  -d '{"qr_token": "eyJhbGci...", "event_id": 1}'
```

## 🔧 Configuration

### Environment Variables
```bash
# Database connection
DATABASE_URL=postgresql://qr_admin:qr_pass@localhost:5432/qr_system

# Authentication settings
API_KEY=test-api-key
SECRET_KEY=your-secret-key-change-in-production

# Multi-tenant settings
ENABLE_MULTI_TENANT=1
ADMIN_PASSWORD=your-secure-admin-password

# QR Code settings
QR_TOKEN_EXPIRE_HOURS=168  # 7 days expiration
```

## 🎯 Key Features

### 1. Platform Agnostic
- RESTful API design supporting any frontend technology
- Standard HTTP interface, easy to integrate

### 2. Offline Support
- Ticket data pre-download
- Offline check-in record caching
- Automatic sync when network recovers

### 3. Security Mechanisms
- JWT Token anti-forgery
- API Key authentication
- Hierarchical permission management
- IP and device information recording

### 4. Scalability
- Modular service layer design
- Clear database architecture
- Support for horizontal scaling

### 5. Multi-Tenant Security
- Complete data isolation between merchants
- Merchant-specific API Keys
- Tenant-aware queries at all levels
- Session management with sessionmaker

## 📈 Performance Metrics

### Test Results
```
🏁 Testing Complete! Passed: 8, Failed: 0
🎉 All tests passed!

✅ Merchant creation and management
✅ API Key generation and validation
✅ Staff multi-tenant isolation
✅ Event multi-tenant isolation
✅ Inter-tenant data isolation
✅ Merchant statistics functionality
✅ API Key permission management
✅ System health checks
```

## 🔮 Future Enhancements

### Potential Feature Additions
1. **Frontend Interface**: React/Vue.js admin interface
2. **Mobile Applications**: iOS/Android scanning apps
3. **Real-time Notifications**: WebSocket real-time updates
4. **Advanced Reports**: More detailed statistical analysis
5. **Multi-language Support**: Internationalization features
6. **API Versioning**: v2 API design

## 📞 Technical Support

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Test Scripts**: Various test scripts in `test_*.sh` and `test_*.py`
- **API Testing Guide**: [API_TESTING_README.md](API_TESTING_README.md)

---

**QR Check-in System v2.0** 🎉  
*Complete Ticket Check-in Solution with Enterprise-Grade Multi-Tenant Architecture*
