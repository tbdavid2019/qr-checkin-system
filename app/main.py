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
    description="QR Code 簽到系統 API"
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
from routers.tickets_simple import router as tickets_router
from routers.checkin_simple import router as checkin_router
from routers.events import router as events_router
from routers.tickets import router as tickets_admin_router
from routers.checkin import router as checkin_admin_router
from routers.merchants import router as merchants_router

app.include_router(staff_router)
app.include_router(tickets_router)
app.include_router(checkin_router)
# 添加管理端API
app.include_router(events_router)
app.include_router(tickets_admin_router, prefix="/admin")
app.include_router(checkin_admin_router, prefix="/admin")
# 添加商戶管理API (僅在多租戶模式下)
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