"""
員工相關 API 路由
"""
from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff
from schemas.staff import StaffLogin, StaffLoginResponse, StaffProfile, StaffEventPermission
from schemas.common import APIResponse
from services.staff_service import StaffService
from utils.auth import create_access_token
from app.config import settings

router = APIRouter(prefix="/api/staff", tags=["Staff"])

@router.post("/login", response_model=StaffLoginResponse)
def staff_login(login_data: StaffLogin, db: Session = Depends(get_db)):
    """員工登入（帳密或登入碼）"""
    staff = StaffService.authenticate_staff(db, login_data)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/password or login code"
        )
    
    # 建立 access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": staff.id}, expires_delta=access_token_expires
    )
    
    return StaffLoginResponse(
        access_token=access_token,
        staff_id=staff.id,
        full_name=staff.full_name
    )

@router.get("/profile", response_model=StaffProfile)
def get_staff_profile(current_staff = Depends(get_current_active_staff)):
    """查詢目前登入員工資訊"""
    return current_staff

@router.get("/events", response_model=List[StaffEventPermission])
def get_staff_events(
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """查詢該員工有權限的活動列表"""
    events = StaffService.get_staff_events(db, current_staff.id)
    return [
        StaffEventPermission(
            event_id=event["event_id"],
            event_name=event["event_name"],
            can_checkin=event["can_checkin"],
            can_revoke=event["can_revoke"]
        )
        for event in events
    ]
