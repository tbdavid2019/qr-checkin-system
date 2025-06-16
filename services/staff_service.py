"""
員工服務
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import Staff, StaffEvent, Event
from schemas.staff import StaffLogin
from utils.security import verify_password, get_password_hash

class StaffService:
    
    @staticmethod
    def authenticate_staff(db: Session, login_data: StaffLogin) -> Optional[Staff]:
        """員工認證"""
        staff = None
        
        if login_data.login_code:
            # 使用登入碼登入
            staff = db.query(Staff).filter(
                Staff.login_code == login_data.login_code,
                Staff.is_active == True
            ).first()
        elif login_data.username and login_data.password:
            # 使用帳號密碼登入
            staff = db.query(Staff).filter(
                Staff.username == login_data.username,
                Staff.is_active == True
            ).first()
            
            if staff and staff.hashed_password:
                if not verify_password(login_data.password, staff.hashed_password):
                    return None
        
        if staff:
            # 更新最後登入時間
            staff.last_login = datetime.utcnow()
            db.commit()
            
        return staff
    
    @staticmethod
    def get_staff_by_id(db: Session, staff_id: int) -> Optional[Staff]:
        """根據 ID 獲取員工"""
        return db.query(Staff).filter(Staff.id == staff_id).first()
    
    @staticmethod
    def get_staff_events(db: Session, staff_id: int) -> List[dict]:
        """獲取員工有權限的活動列表"""
        staff_events = (db.query(StaffEvent, Event)
                       .join(Event, StaffEvent.event_id == Event.id)
                       .filter(StaffEvent.staff_id == staff_id)
                       .filter(Event.is_active == True)
                       .all())
        
        result = []
        for staff_event, event in staff_events:
            result.append({
                "event_id": event.id,
                "event_name": event.name,
                "event_start_time": event.start_time,
                "event_end_time": event.end_time,
                "can_checkin": staff_event.can_checkin,
                "can_revoke": staff_event.can_revoke
            })
        
        return result
    
    @staticmethod
    def can_access_event(db: Session, staff_id: int, event_id: int) -> bool:
        """檢查員工是否有權限存取活動"""
        staff_event = (db.query(StaffEvent)
                      .filter(StaffEvent.staff_id == staff_id)
                      .filter(StaffEvent.event_id == event_id)
                      .first())
        
        return staff_event is not None
    
    @staticmethod
    def can_checkin(db: Session, staff_id: int, event_id: int) -> bool:
        """檢查員工是否有簽到權限"""
        staff_event = (db.query(StaffEvent)
                      .filter(StaffEvent.staff_id == staff_id)
                      .filter(StaffEvent.event_id == event_id)
                      .first())
        
        return staff_event and staff_event.can_checkin
    
    @staticmethod
    def can_revoke(db: Session, staff_id: int, event_id: int) -> bool:
        """檢查員工是否有撤銷簽到權限"""
        staff_event = (db.query(StaffEvent)
                      .filter(StaffEvent.staff_id == staff_id)
                      .filter(StaffEvent.event_id == event_id)
                      .first())
        
        return staff_event and staff_event.can_revoke
    
    @staticmethod
    def create_staff(db: Session, staff_data, merchant_id: Optional[int] = None) -> Staff:
        """創建新員工"""
        # 檢查用戶名是否已存在
        existing_staff = db.query(Staff).filter(Staff.username == staff_data.username).first()
        if existing_staff:
            raise ValueError(f"用戶名 '{staff_data.username}' 已存在")
        
        # 創建新員工
        hashed_password = get_password_hash(staff_data.password)
        
        # 根據 role 設置 is_admin
        is_admin = getattr(staff_data, 'role', 'staff') == 'admin'
        
        staff = Staff(
            username=staff_data.username,
            hashed_password=hashed_password,
            full_name=staff_data.name,
            email=staff_data.email,
            is_admin=is_admin,
            merchant_id=merchant_id,
            is_active=True
        )
        
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff
    
    @staticmethod
    def get_staff_by_username(db: Session, username: str) -> Optional[Staff]:
        """根據用戶名獲取員工"""
        return db.query(Staff).filter(Staff.username == username).first()
    
    @staticmethod
    def get_staff_by_merchant(db: Session, merchant_id: int) -> List[Staff]:
        """獲取指定商戶的所有員工"""
        return db.query(Staff).filter(Staff.merchant_id == merchant_id).all()
    
    @staticmethod
    def update_staff(db: Session, staff_id: int, staff_data) -> Staff:
        """更新員工資訊"""
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise ValueError(f"員工 ID {staff_id} 不存在")
        
        # 檢查用戶名是否被其他員工使用
        if hasattr(staff_data, 'username') and staff_data.username != staff.username:
            existing_staff = db.query(Staff).filter(
                Staff.username == staff_data.username,
                Staff.id != staff_id
            ).first()
            if existing_staff:
                raise ValueError(f"用戶名 '{staff_data.username}' 已被其他員工使用")
        
        # 更新員工資訊
        if hasattr(staff_data, 'username'):
            staff.username = staff_data.username
        if hasattr(staff_data, 'name'):
            staff.full_name = staff_data.name
        if hasattr(staff_data, 'email'):
            staff.email = staff_data.email
        if hasattr(staff_data, 'password') and staff_data.password:
            staff.hashed_password = get_password_hash(staff_data.password)
        if hasattr(staff_data, 'role'):
            staff.is_admin = staff_data.role == 'admin'
        
        db.commit()
        db.refresh(staff)
        return staff
    
    @staticmethod
    def delete_staff(db: Session, staff_id: int) -> bool:
        """刪除員工"""
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            return False
        
        try:
            # 先刪除相關的員工活動權限記錄
            db.query(StaffEvent).filter(StaffEvent.staff_id == staff_id).delete()
            
            # 刪除員工
            db.delete(staff)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
