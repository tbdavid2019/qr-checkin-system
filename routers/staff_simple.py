"""
簡化版員工認證 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff, require_api_key, get_current_merchant
from schemas.staff import StaffLogin, StaffCreate, StaffProfile
from services.staff_service import StaffService
from app.config import settings

router = APIRouter(prefix="/api/staff", tags=["Staff"])

@router.post("/verify")
def verify_staff(login_data: StaffLogin, db: Session = Depends(get_db)):
    """員工驗證（帳密或登入碼）- 返回員工ID"""
    staff = StaffService.authenticate_staff(db, login_data)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/password or login code"
        )
    
    return {
        "success": True,
        "staff_id": staff.id,
        "full_name": staff.full_name,
        "message": "Authentication successful"
    }

@router.get("/profile")
def get_profile(
    current_staff = Depends(get_current_active_staff)
):
    """獲取當前員工資料"""
    return {
        "staff_id": current_staff.id,
        "username": current_staff.username,
        "full_name": current_staff.full_name,
        "is_active": current_staff.is_active,
        "is_admin": current_staff.is_admin
    }

@router.get("/events")
def get_staff_events(
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """查詢該員工有權限的活動列表"""
    events = StaffService.get_staff_events(db, current_staff.id)
    return [
        {
            "event_id": event["event_id"],
            "event_name": event["event_name"],
            "can_checkin": event["can_checkin"],
            "can_revoke": event["can_revoke"]
        }
        for event in events
    ]

@router.post("/create", response_model=StaffProfile)
def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    x_api_key: str = Header(None)
):
    """創建新員工（多租戶模式下使用商戶API Key）"""
    try:
        merchant_id = None
        
        # 檢查是否啟用多租戶模式
        if settings.ENABLE_MULTI_TENANT:
            if not x_api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing API key"
                )
            
            # 在多租戶模式下，使用API Key查找商戶
            from services.merchant_service import MerchantService
            merchant = MerchantService.get_merchant_by_api_key(db, x_api_key)
            if not merchant or not merchant.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or inactive merchant API key"
                )
            merchant_id = merchant.id
        else:
            # 單租戶模式：使用固定API Key
            if x_api_key != settings.API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
        
        staff = StaffService.create_staff(db, staff_data, merchant_id)
        
        return StaffProfile(
            id=staff.id,
            username=staff.username,
            email=staff.email,
            full_name=staff.full_name,
            is_active=staff.is_active,
            is_admin=staff.is_admin,
            last_login=staff.last_login
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
