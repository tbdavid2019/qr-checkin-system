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
