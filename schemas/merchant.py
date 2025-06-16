"""
商戶相關的 Pydantic schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class MerchantBase(BaseModel):
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class MerchantCreate(MerchantBase):
    pass

class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None

class Merchant(MerchantBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ApiKeyBase(BaseModel):
    key_name: str
    permissions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

class ApiKeyCreate(BaseModel):
    key_name: str
    permissions: Optional[Dict[str, Any]] = None
    expires_days: Optional[int] = None  # 改為天數，而不是具體時間

class ApiKeyResponse(BaseModel):
    id: int
    merchant_id: int
    key_name: str
    api_key: str
    permissions: Optional[Dict[str, Any]]
    expires_at: Optional[datetime]
    is_active: bool
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApiKeyWithSecret(ApiKeyResponse):
    """只在創建時返回，包含完整的API Key"""
    api_key_full: str

class MerchantWithStats(Merchant):
    """包含統計資訊的商戶資料"""
    total_events: int = 0
    total_tickets: int = 0
    total_staff: int = 0
    active_api_keys: int = 0
