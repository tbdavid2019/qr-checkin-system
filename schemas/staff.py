"""
員工相關的 Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class StaffLogin(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    login_code: Optional[str] = None  # 簡易登入碼

class StaffLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    staff_id: int
    full_name: str

class StaffProfile(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: str
    is_active: bool
    is_admin: bool
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class StaffEventPermission(BaseModel):
    event_id: int
    event_name: str
    can_checkin: bool
    can_revoke: bool

class StaffEventAssign(BaseModel):
    staff_id: int
    event_id: int
    can_checkin: bool = True
    can_revoke: bool = False

class StaffEventPermissionResponse(StaffEventPermission):
    staff_id: int
    
    class Config:
        from_attributes = True

class StaffCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: Optional[str] = None
    role: str = "staff"  # staff 或 admin

class StaffUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
