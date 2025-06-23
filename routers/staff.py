"""
員工身份驗證與個人資料 API
"""
from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
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
