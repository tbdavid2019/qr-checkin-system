"""
配置文件
"""
import os
from typing import Optional

class Settings:
    # 資料庫配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://qr_admin:qr_pass@localhost:5432/qr_system"
    )
    
    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 天
    
    # API 配置
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "QR Check-in System"
    VERSION: str = "1.0.0"
    API_KEY: str = os.getenv("API_KEY", "test-api-key")  # 簡化認證用的API Key
    
    # 多租戶配置
    ENABLE_MULTI_TENANT: bool = os.getenv("ENABLE_MULTI_TENANT", "1") == "1"
    
    # Gradio 管理介面配置
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    GRADIO_PORT: int = int(os.getenv("GRADIO_PORT", "7860"))
    
    # 跨域配置 - 暫時允許所有來源
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # QR Code 配置
    QR_TOKEN_EXPIRE_HOURS: int = 24 * 7  # QR Code Token 7 天過期

settings = Settings()
