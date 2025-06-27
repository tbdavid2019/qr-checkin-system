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
        """根據 ID 獲取員工（通用，無商戶限制）"""
        return db.query(Staff).filter(Staff.id == staff_id).first()
    
    @staticmethod
    def get_staff_events(db: Session, staff_id: int) -> List[dict]:
        """獲取員工可存取的活動列表（商戶下近期活動）"""
        from datetime import datetime, timedelta
        
        # 先獲取員工資訊
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff or not staff.merchant_id:
            return []
        
        # 計算時間範圍
        now = datetime.now()
        today = now.date()
        
        # 活動開始時間：今天開始到未來30天內
        start_filter_min = datetime.combine(today, datetime.min.time())
        start_filter_max = start_filter_min + timedelta(days=30)
        
        # 活動結束時間：不能早於昨天（活動結束後1天內仍可見）
        end_filter_min = now - timedelta(days=1)
        
        # 查詢該商戶下符合時間條件的活動
        events = (db.query(Event)
                 .filter(Event.merchant_id == staff.merchant_id)
                 .filter(Event.is_active == True)
                 .filter(Event.start_time >= start_filter_min)
                 .filter(Event.start_time <= start_filter_max)
                 .filter(Event.end_time >= end_filter_min)
                 .order_by(Event.start_time.asc())
                 .all())
        
        result = []
        for event in events:
            # 檢查是否有特定權限設定
            staff_event = (db.query(StaffEvent)
                          .filter(StaffEvent.staff_id == staff_id)
                          .filter(StaffEvent.event_id == event.id)
                          .first())
            
            # 如果有特定權限設定則使用，否則預設為可簽到但不可撤銷
            can_checkin = staff_event.can_checkin if staff_event else True
            can_revoke = staff_event.can_revoke if staff_event else False
            
            result.append({
                "event_id": event.id,
                "event_name": event.name,
                "event_start_time": event.start_time,
                "event_end_time": event.end_time,
                "can_checkin": can_checkin,
                "can_revoke": can_revoke
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
    def assign_event_to_staff(db: Session, assignment: 'StaffEventAssign') -> StaffEvent:
        """指派活動權限給員工"""
        # 檢查員工與活動是否存在
        staff = db.query(Staff).filter(Staff.id == assignment.staff_id).first()
        if not staff:
            raise ValueError(f"員工 ID {assignment.staff_id} 不存在")
        
        event = db.query(Event).filter(Event.id == assignment.event_id).first()
        if not event:
            raise ValueError(f"活動 ID {assignment.event_id} 不存在")

        # 檢查是否已存在相同的權限設定
        existing_permission = db.query(StaffEvent).filter_by(
            staff_id=assignment.staff_id,
            event_id=assignment.event_id
        ).first()

        if existing_permission:
            # 更新現有權限
            existing_permission.can_checkin = assignment.can_checkin
            existing_permission.can_revoke = assignment.can_revoke
            db.commit()
            db.refresh(existing_permission)
            return existing_permission
        else:
            # 建立新的權限
            new_permission = StaffEvent(
                staff_id=assignment.staff_id,
                event_id=assignment.event_id,
                can_checkin=assignment.can_checkin,
                can_revoke=assignment.can_revoke
            )
            db.add(new_permission)
            db.commit()
            db.refresh(new_permission)
            return new_permission

    @staticmethod
    def create_staff(db: Session, staff_data, merchant_id: Optional[int] = None) -> Staff:
        """創建新員工"""
        # 檢查用戶名是否已存在
        existing_staff = db.query(Staff).filter(Staff.username == staff_data.username).first()
        if existing_staff:
            raise ValueError(f"用戶名 '{staff_data.username}' 已存在")
        
        # 檢查 email 是否已存在（如果提供了 email）
        if staff_data.email:
            existing_email = db.query(Staff).filter(Staff.email == staff_data.email).first()
            if existing_email:
                raise ValueError(f"Email '{staff_data.email}' 已被其他員工使用")
        
        # 創建新員工
        hashed_password = get_password_hash(staff_data.password)
        
        # 根據 role 設置 is_admin
        is_admin = getattr(staff_data, 'role', 'staff') == 'admin'
        
        staff = Staff(
            username=staff_data.username,
            hashed_password=hashed_password,
            full_name=staff_data.full_name,
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
    def update_staff(db: Session, staff_id: int, staff_data, merchant_id: int) -> Staff:
        """更新員工資訊（會驗證商戶所有權）"""
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff or staff.merchant_id != merchant_id:
            raise ValueError(f"員工 ID {staff_id} 在此商戶下不存在")
        
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
        if hasattr(staff_data, 'full_name'):
            staff.full_name = staff_data.full_name
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
    def delete_staff(db: Session, staff_id: int, merchant_id: int) -> bool:
        """刪除員工（會驗證商戶所有權）"""
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise ValueError(f"員工 ID {staff_id} 不存在")
        if staff.merchant_id != merchant_id:
            raise ValueError(f"員工 ID {staff_id} 不屬於此商戶")
        
        try:
            # 先刪除相關的員工活動權限記錄
            deleted_permissions = db.query(StaffEvent).filter(StaffEvent.staff_id == staff_id).delete()
            
            # 檢查是否有簽到記錄（如果有，可能需要處理）
            from models.checkin import CheckinLog
            checkin_count = db.query(CheckinLog).filter(CheckinLog.staff_id == staff_id).count()
            if checkin_count > 0:
                # 如果有簽到記錄，我們不刪除員工，只是將其設為非活躍
                staff.is_active = False
                db.commit()
                return True
            
            # 刪除員工
            db.delete(staff)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise ValueError(f"刪除員工失敗: {str(e)}")
