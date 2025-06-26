"""
員工身份驗證與個人資料 API
"""
from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff
from schemas.staff import StaffLogin, StaffLoginResponse, StaffProfile, StaffEventPermission
from services.staff_service import StaffService
from utils.auth import create_access_token
from app.config import settings

router = APIRouter(prefix="/api/v1/staff", tags=["Staff: Auth & Profile"])

@router.post("/login", response_model=StaffLoginResponse, summary="Staff Login")
def staff_login(login_data: StaffLogin, db: Session = Depends(get_db)):
    """
    Staff login with username/password or a temporary login code.
    """
    staff = StaffService.authenticate_staff(db, login_data)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/password or login code"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(staff.id), "type": "staff"}, expires_delta=access_token_expires
    )
    
    return StaffLoginResponse(
        access_token=access_token,
        staff_id=staff.id,
        full_name=staff.full_name
    )

@router.get("/me/profile", response_model=StaffProfile, summary="Get Own Profile")
def get_staff_profile(current_staff: StaffProfile = Depends(get_current_active_staff)):
    """
    Get the profile of the currently logged-in staff member.
    """
    return current_staff

@router.get("/me/events", response_model=List[StaffEventPermission], summary="Get Own Event Permissions")
def get_staff_events(
    current_staff: StaffProfile = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """
    Get the list of events the currently logged-in staff member has permissions for.
    
    **時間過濾規則：**
    - 只顯示近期相關的活動，避免顯示過多歷史活動
    - 活動開始時間：今天到未來30天內
    - 活動結束時間：不早於昨天（活動結束後1天內仍可見）
    - 這樣的設計方便會前準備和事後統計
    
    **權限說明：**
    - 若員工有特定活動權限設定，則依據設定
    - 若無特定設定，預設為可簽到但不可撤銷
    """
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
