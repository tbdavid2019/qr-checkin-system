"""
簡化版員工認證 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff, require_api_key
from schemas.staff import StaffLogin
from services.staff_service import StaffService

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
