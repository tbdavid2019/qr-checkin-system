"""
商戶相關模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base

class Merchant(Base):
    """商戶模型"""
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 關聯
    api_keys = relationship("ApiKey", back_populates="merchant")
    events = relationship("Event", back_populates="merchant")
    staff = relationship("Staff", back_populates="merchant")

class ApiKey(Base):
    """API Key模型"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    key_name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    permissions = Column(JSON, nullable=True)  # 權限設定
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 關聯
    merchant = relationship("Merchant", back_populates="api_keys")
