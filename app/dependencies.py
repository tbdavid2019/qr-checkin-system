"""
認證相關依賴項 - 簡化版本
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings

def get_current_active_staff(
    x_api_key: Optional[str] = Header(None),
    staff_id: Optional[int] = Header(None),
    db: Session = Depends(get_db)
):
    """簡化版員工認證 - 只需要API Key和Staff ID"""
    # 檢查API Key
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # 檢查Staff ID
    if not staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing staff ID in header"
        )
    
    # 延遲導入以避免循環導入
    from services.staff_service import StaffService
    
    staff = StaffService.get_staff_by_id(db, staff_id)
    if not staff or not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive staff"
        )
    
    return staff

def require_api_key(x_api_key: Optional[str] = Header(None)):
    """API Key 驗證（用於受保護的管理端點）"""
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True
