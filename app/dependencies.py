"""
認證相關依賴項 - 支援多租戶模式
"""
from typing import Optional, Tuple
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from models.merchant import Merchant
from models.staff import Staff

def get_merchant_and_staff(
    x_api_key: Optional[str] = Header(None),
    staff_id: Optional[int] = Header(None),
    db: Session = Depends(get_db)
) -> Tuple[Optional[Merchant], Staff]:
    """獲取商戶和員工資訊"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    if not staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing staff ID in header"
        )
    
    # 延遲導入以避免循環導入
    from services.staff_service import StaffService
    from services.merchant_service import MerchantService
    
    merchant = None
    
    # 檢查是否啟用多租戶模式
    if settings.ENABLE_MULTI_TENANT:
        # 多租戶模式：使用API Key查找商戶
        merchant = MerchantService.get_merchant_by_api_key(db, x_api_key)
        if not merchant or not merchant.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive merchant API key"
            )
        
        # 驗證員工屬於該商戶
        staff = StaffService.get_staff_by_id(db, staff_id)
        if not staff or not staff.is_active or staff.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or unauthorized staff"
            )
    else:
        # 單租戶模式：使用固定API Key
        if x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        staff = StaffService.get_staff_by_id(db, staff_id)
        if not staff or not staff.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive staff"
            )
    
    return merchant, staff

def get_current_active_staff(
    merchant_staff: Tuple[Optional[Merchant], Staff] = Depends(get_merchant_and_staff)
) -> Staff:
    """獲取當前活躍員工"""
    merchant, staff = merchant_staff
    return staff

def get_current_merchant(
    merchant_staff: Tuple[Optional[Merchant], Staff] = Depends(get_merchant_and_staff)
) -> Optional[Merchant]:
    """獲取當前商戶（多租戶模式下）"""
    merchant, staff = merchant_staff
    return merchant

def require_api_key(x_api_key: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """API Key 驗證（用於受保護的管理端點）"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    if settings.ENABLE_MULTI_TENANT:
        from services.merchant_service import MerchantService
        merchant = MerchantService.get_merchant_by_api_key(db, x_api_key)
        if not merchant or not merchant.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive merchant API key"
            )
        return merchant
    else:
        if x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        return True

def require_super_admin(x_api_key: Optional[str] = Header(None)):
    """超級管理員認證（用於商戶管理端點）"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    # 在多租戶模式下，只有系統預設的 API Key 可以管理商戶
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Super admin access required"
        )
    
    return True

def require_admin_api_key(x_api_key: Optional[str] = Header(None)):
    """超級管理員API Key驗證（用於商戶管理）"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    # 在多租戶模式下，商戶管理使用特殊的管理員API Key
    if settings.ENABLE_MULTI_TENANT:
        # 使用固定的管理員API Key進行商戶管理
        if x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin API key"
            )
    else:
        if x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    return True
