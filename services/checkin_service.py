"""
簽到服務
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import CheckInLog, Ticket, Staff
from schemas.checkin import CheckInRequest, OfflineCheckInSync
from services.ticket_service import TicketService

class CheckInService:
    
    @staticmethod
    def check_in_ticket(
        db: Session, 
        ticket_id: int, 
        staff_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> CheckInLog:
        """簽到票券"""
        # 標記票券為已使用
        TicketService.mark_ticket_used(db, ticket_id)
        
        # 建立簽到記錄
        checkin_log = CheckInLog(
            ticket_id=ticket_id,
            staff_id=staff_id,
            ip_address=ip_address,
            user_agent=user_agent,
            checkin_time=datetime.utcnow()
        )
        db.add(checkin_log)
        db.commit()
        db.refresh(checkin_log)
        return checkin_log
    
    @staticmethod
    def get_checkin_log_by_id(db: Session, checkin_log_id: int) -> Optional[CheckInLog]:
        """Get a check-in log by its ID."""
        return db.query(CheckInLog).filter(CheckInLog.id == checkin_log_id).first()

    @staticmethod
    def revoke_checkin(
        db: Session, 
        checkin_log_id: int, 
        revoked_by_staff_id: int
    ) -> Optional[CheckInLog]:
        """撤銷簽到"""
        checkin_log = db.query(CheckInLog).filter(CheckInLog.id == checkin_log_id).first()
        if not checkin_log:
            return None
        
        # 標記為已撤銷
        checkin_log.is_revoked = True
        checkin_log.revoked_by = revoked_by_staff_id
        checkin_log.revoked_at = datetime.utcnow()
        
        # 將票券標記為未使用
        ticket = db.query(Ticket).filter(Ticket.id == checkin_log.ticket_id).first()
        if ticket:
            ticket.is_used = False
        
        db.commit()
        db.refresh(checkin_log)
        return checkin_log
    
    @staticmethod
    def get_checkin_logs_by_event(
        db: Session,
        event_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """獲取活動的簽到記錄（包含票券和員工資訊）"""
        # 驗證分頁參數
        skip = max(0, skip)  # 確保 skip 不是負數
        limit = max(1, min(100, limit))  # 確保 limit 在 1-100 之間
        
        logs = (db.query(CheckInLog)
                .join(Ticket, CheckInLog.ticket_id == Ticket.id)
                .filter(Ticket.event_id == event_id)
                .offset(skip)
                .limit(limit)
                .all())
        
        result = []
        for log in logs:
            # 獲取票券資訊
            ticket = db.query(Ticket).filter(Ticket.id == log.ticket_id).first()
            ticket_info = {
                "id": ticket.id,
                "uuid": str(ticket.uuid),
                "holder_name": ticket.holder_name,
                "ticket_code": ticket.ticket_code,
                "is_used": ticket.is_used
            } if ticket else None
            
            # 獲取員工資訊
            staff_info = None
            if log.staff_id:
                staff = db.query(Staff).filter(Staff.id == log.staff_id).first()
                if staff:
                    staff_info = {
                        "id": staff.id,
                        "username": staff.username,
                        "full_name": staff.full_name
                    }
            
            log_detail = {
                "id": log.id,
                "ticket_id": log.ticket_id,
                "staff_id": log.staff_id,
                "checkin_time": log.checkin_time,
                "is_revoked": log.is_revoked,
                "revoked_at": log.revoked_at,
                "ticket": ticket_info,
                "staff": staff_info
            }
            result.append(log_detail)
        
        return result
    
    @staticmethod
    def sync_offline_checkins(db: Session, sync_data: OfflineCheckInSync, staff_id: int) -> List[CheckInLog]:
        """同步離線簽到記錄"""
        checkin_logs = []
        
        for offline_checkin in sync_data.checkins:
            # 檢查票券是否已經簽到過
            existing_checkin = (db.query(CheckInLog)
                              .filter(CheckInLog.ticket_id == offline_checkin.ticket_id)
                              .filter(CheckInLog.is_revoked == False)
                              .first())
            
            if existing_checkin:
                continue  # 跳過已簽到的票券
            
            # 建立簽到記錄
            checkin_log = CheckInLog(
                ticket_id=offline_checkin.ticket_id,
                staff_id=staff_id,
                checkin_time=offline_checkin.checkin_time
            )
            db.add(checkin_log)
            checkin_logs.append(checkin_log)
            
            # 標記票券為已使用
            TicketService.mark_ticket_used(db, offline_checkin.ticket_id)
        
        db.commit()
        for log in checkin_logs:
            db.refresh(log)
        
        return checkin_logs
