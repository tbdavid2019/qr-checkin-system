"""
商戶管理路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin_password
from schemas.merchant import (
    Merchant, MerchantCreate, MerchantUpdate, 
    ApiKeyResponse, ApiKeyCreate, MerchantCreateResponse
)
from services.merchant_service import MerchantService

router = APIRouter(prefix="/admin/merchants", tags=["Admin: Merchants"])

@router.post("", response_model=MerchantCreateResponse)
async def create_merchant(
    merchant_data: MerchantCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """創建新商戶"""
    return MerchantService.create_merchant(db, merchant_data)

@router.get("", response_model=List[Merchant])
async def get_merchants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """獲取商戶列表"""
    return MerchantService.get_merchants(db, skip=skip, limit=limit)

@router.get("/{merchant_id}", response_model=Merchant)
async def get_merchant(
    merchant_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """獲取商戶詳情"""
    merchant = MerchantService.get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    return merchant

@router.put("/{merchant_id}", response_model=Merchant)
async def update_merchant(
    merchant_id: int,
    merchant_data: MerchantUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """更新商戶資訊"""
    merchant = MerchantService.update_merchant(db, merchant_id, merchant_data)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    return merchant

@router.post("/{merchant_id}/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    merchant_id: int,
    api_key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """為商戶創建API Key"""
    # 檢查商戶是否存在
    merchant = MerchantService.get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    api_key = MerchantService.create_api_key(
        db=db,
        merchant_id=merchant_id,
        key_name=api_key_data.key_name,
        permissions=api_key_data.permissions,
        expires_days=api_key_data.expires_days
    )
    
    return api_key

@router.get("/{merchant_id}/api-keys", response_model=List[ApiKeyResponse])
async def get_merchant_api_keys(
    merchant_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """獲取商戶的API Keys"""
    return MerchantService.get_merchant_api_keys(db, merchant_id)

@router.delete("/{merchant_id}/api-keys/{api_key_id}")
async def revoke_api_key(
    merchant_id: int,
    api_key_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """撤銷API Key"""
    success = MerchantService.revoke_api_key(db, api_key_id, merchant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key revoked successfully"}

@router.get("/{merchant_id}/statistics")
async def get_merchant_statistics(
    merchant_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin_password)
):
    """獲取商戶統計資訊"""
    # 檢查商戶是否存在
    merchant = MerchantService.get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )
    
    return MerchantService.get_merchant_statistics(db, merchant_id)
