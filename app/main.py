"""
QR Check-in System Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from routers.staff_simple import router as staff_router
from routers.tickets_simple import router as tickets_router

# 建立 FastAPI 應用程式
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
QR Code 簽到系統 API

## API 架構說明

### 商戶/外部系統使用的 API
- **`/api/staff/*`** - 員工認證與管理
- **`/api/tickets/*`** - 票券公開功能（QR Code生成、驗證）
- **`/api/checkin/*`** - 簽到功能
- **`/api/events/*`** - 活動管理（商戶專用，需要 API Key）
- **`/api/tickets-mgmt/*`** - 票券管理（商戶專用，需要 API Key）
- **`/api/checkin-mgmt/*`** - 簽到管理（商戶專用，需要 API Key）

### 管理端 API (Gradio 使用)
- **`/admin/merchants/*`** - 商戶管理（僅超級管理員）

## 認證方式

### 商戶 API Key 認證
需要在 Header 中包含：
```
X-API-Key: qr_xxx...  # 商戶專屬 API Key
Staff-ID: 1           # 員工 ID（某些端點需要）
```

### 超級管理員認證
需要在 Header 中包含：
```
X-Admin-Password: your-admin-password
```

## Ticket Description 欄位說明
票券現在支援 `description` 欄位，可存儲 JSON 格式的額外資訊：
```json
{
  "seat": "A-01",
  "zone": "VIP", 
  "entrance": "Gate A",
  "meal": "vegetarian",
  "accessibility": "wheelchair"
}
```

## 票券產生流程
要使用票券管理功能，請依照以下流程操作：

### 1. 建立商戶 (由管理員執行)
使用 `/admin/merchants/` API 建立商戶並取得 API Key

### 2. 建立活動
使用商戶 API Key 呼叫 `/api/events/` 建立活動

### 3. 建立票種 (重要步驟)
⚠️ **在產票之前，必須先建立票種！**
使用 `/api/events/{event_id}/ticket-types/` 建立票種

### 4. 產生票券
使用票種 ID 透過以下 API 產生票券：
- **批次產票**: `/api/tickets-mgmt/batch`
- **單筆產票**: `/api/tickets-mgmt/`

### 5. 生成 QR Code
使用 `/api/tickets/{ticket_id}/qrcode` 取得票券 QR Code

### 6. 簽到驗證
使用 `/api/checkin/check` 進行票券簽到
    """,
    openapi_tags=[
        {
            "name": "Staff",
            "description": "員工認證與管理"
        },
        {
            "name": "Tickets", 
            "description": "票券公開功能 - QR Code生成與驗證（無需認證）"
        },
        {
            "name": "Check-in",
            "description": "簽到功能"
        },
        {
            "name": "Events",
            "description": "活動管理（商戶專用，需要 API Key）"
        },
        {
            "name": "Tickets Management",
            "description": "票券管理 CRUD 操作（商戶專用，需要 API Key）"
        },
        {
            "name": "Check-in Management", 
            "description": "簽到管理功能（商戶專用，需要 API Key）"
        },
        {
            "name": "merchants",
            "description": "商戶管理（僅超級管理員）"
        }
    ]
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
from routers.staff_simple import router as staff_router
from routers.tickets_simple import router as tickets_public_router  # 公開票券 API
from routers.checkin_simple import router as checkin_router
from routers.events import router as events_router
from routers.tickets import router as tickets_merchant_router  # 商戶票券管理 API
from routers.checkin import router as checkin_admin_router
from routers.merchants import router as merchants_router

# 公開 API（不需要額外前綴，路由文件已有 /api/ 前綴）
app.include_router(staff_router)
app.include_router(tickets_public_router)  # 公開票券路由（QR Code生成、驗證）
app.include_router(checkin_router)

# 商戶專用 API（需要 API Key）
app.include_router(events_router)  # 活動管理
app.include_router(tickets_merchant_router)  # 票券 CRUD 管理
app.include_router(checkin_admin_router)  # 簽到管理功能

# 管理端 API (僅在多租戶模式下，需要 /admin 前綴)
if settings.ENABLE_MULTI_TENANT:
    app.include_router(merchants_router, prefix="/admin")

@app.get("/")
def read_root():
    """根路由"""
    return {
        "message": "QR Check-in System API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)