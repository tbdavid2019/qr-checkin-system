"""
商戶管理服務
"""
import secrets
import string
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.merchant import Merchant, ApiKey
from models.event import Event
from models.ticket import Ticket
from models.staff import Staff
from schemas.merchant import MerchantCreate, MerchantUpdate, ApiKeyCreate
from app.config import settings

class MerchantService:
    
    @staticmethod
    def generate_api_key() -> str:
        """生成安全的API Key"""
        # 生成32字符的隨機字符串
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        return f"qr_{api_key}"
    
    @staticmethod
    def create_merchant(db: Session, merchant_data: MerchantCreate) -> dict:
        """創建新商戶並返回包含 API Key 的資訊"""
        merchant = Merchant(**merchant_data.dict())
        db.add(merchant)
        db.commit()
        db.refresh(merchant)

        # 創建一個預設的 API Key
        api_key_record = MerchantService.create_api_key(
            db=db,
            merchant_id=merchant.id,
            key_name="Default Key"
        )

        # 將 merchant 物件轉為字典，並加入 api_key
        response_data = {c.name: getattr(merchant, c.name) for c in merchant.__table__.columns}
        response_data['api_key'] = api_key_record.api_key
        
        return response_data
    
    @staticmethod
    def get_merchant_by_id(db: Session, merchant_id: int) -> Optional[Merchant]:
        """根據ID獲取商戶"""
        return db.query(Merchant).filter(Merchant.id == merchant_id).first()
    
    @staticmethod
    def get_merchants(db: Session, skip: int = 0, limit: int = 100) -> List[Merchant]:
        """獲取商戶列表"""
        # 驗證分頁參數
        skip = max(0, skip)  # 確保 skip 不是負數
        limit = max(1, min(100, limit))  # 確保 limit 在 1-100 之間
        
        return db.query(Merchant).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_merchant(db: Session, merchant_id: int, merchant_data: MerchantUpdate) -> Optional[Merchant]:
        """更新商戶資訊"""
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return None
        
        update_data = merchant_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(merchant, field, value)
        
        merchant.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(merchant)
        return merchant
    
    @staticmethod
    def create_api_key(
        db: Session, 
        merchant_id: int, 
        key_name: str,
        permissions: Optional[dict] = None,
        expires_days: Optional[int] = None
    ) -> ApiKey:
        """為商戶創建API Key"""
        api_key = MerchantService.generate_api_key()
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key_record = ApiKey(
            merchant_id=merchant_id,
            key_name=key_name,
            api_key=api_key,
            permissions=permissions or {
                "events": ["read", "write"],
                "tickets": ["read", "write"],
                "staff": ["read"]
            },
            expires_at=expires_at
        )
        
        db.add(api_key_record)
        db.commit()
        db.refresh(api_key_record)
        return api_key_record
    
    @staticmethod
    def get_merchant_by_api_key(db: Session, api_key: str) -> Optional[Merchant]:
        """根據API Key獲取商戶"""
        api_key_record = db.query(ApiKey).filter(
            ApiKey.api_key == api_key,
            ApiKey.is_active == True
        ).first()
        
        if not api_key_record:
            return None
        
        # 檢查是否過期
        if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
            return None
        
        # 更新使用統計
        api_key_record.last_used_at = datetime.utcnow()
        api_key_record.usage_count += 1
        db.commit()
        
        return api_key_record.merchant
    
    @staticmethod
    def get_merchant_api_keys(db: Session, merchant_id: int) -> List[ApiKey]:
        """獲取商戶的所有API Keys"""
        return db.query(ApiKey).filter(ApiKey.merchant_id == merchant_id).all()
    
    @staticmethod
    def revoke_api_key(db: Session, api_key_id: int, merchant_id: int) -> bool:
        """撤銷API Key"""
        api_key = db.query(ApiKey).filter(
            ApiKey.id == api_key_id,
            ApiKey.merchant_id == merchant_id
        ).first()
        
        if not api_key:
            return False
        
        api_key.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_merchant_statistics(db: Session, merchant_id: int) -> dict:
        """獲取商戶統計資訊"""
        total_events = db.query(Event).filter(Event.merchant_id == merchant_id).count()
        total_tickets = (db.query(Ticket)
                        .join(Event, Ticket.event_id == Event.id)
                        .filter(Event.merchant_id == merchant_id)
                        .count())
        total_staff = db.query(Staff).filter(Staff.merchant_id == merchant_id).count()
        active_api_keys = db.query(ApiKey).filter(
            ApiKey.merchant_id == merchant_id,
            ApiKey.is_active == True
        ).count()
        
        return {
            "total_events": total_events,
            "total_tickets": total_tickets,
            "total_staff": total_staff,
            "active_api_keys": active_api_keys
        }
    
    @staticmethod
    def is_multi_tenant_enabled() -> bool:
        """檢查是否啟用多租戶模式"""
        return settings.ENABLE_MULTI_TENANT
