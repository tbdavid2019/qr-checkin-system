"""
數據庫連接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """依賴注入：獲取數據庫 session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
