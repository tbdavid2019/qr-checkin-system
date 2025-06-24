"""
活動服務
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Event, TicketType, Ticket
from schemas.event import EventCreate, EventUpdate, TicketTypeCreate, TicketTypeUpdate

class EventService:
    
    @staticmethod
    def create_event(db: Session, event_data: EventCreate, merchant_id: Optional[int] = None) -> Event:
        """建立活動（支援多租戶）"""
        event_dict = event_data.dict()
        print(f"🔧 [DEBUG] 活動創建資料: {event_dict}")  # 調試輸出
        if merchant_id:
            event_dict['merchant_id'] = merchant_id
        
        event = Event(**event_dict)
        print(f"🔧 [DEBUG] 建立的活動物件: total_quota={event.total_quota}")  # 調試輸出
        db.add(event)
        db.commit()
        db.refresh(event)
        print(f"🔧 [DEBUG] 儲存後的活動物件: total_quota={event.total_quota}")  # 調試輸出
        
        # 自動建立預設票種
        EventService._create_default_ticket_type(db, event)
        
        return event
    
    @staticmethod
    def _create_default_ticket_type(db: Session, event: Event) -> TicketType:
        """為活動建立預設票種"""
        # 檢查是否已經有票種
        existing_ticket_types = db.query(TicketType).filter(TicketType.event_id == event.id).count()
        if existing_ticket_types > 0:
            return None  # 已有票種，不建立預設票種
        
        # 建立預設票種，配額設為活動總配額（如果有設定的話）
        default_quota = event.total_quota if event.total_quota and event.total_quota > 0 else 0
        
        default_ticket_type = TicketType(
            event_id=event.id,
            name="一般票",
            quota=default_quota,
            is_active=True
        )
        
        db.add(default_ticket_type)
        db.commit()
        db.refresh(default_ticket_type)
        
        print(f"🎫 [INFO] 為活動 {event.id} 建立預設票種: {default_ticket_type.name} (配額: {default_quota})")
        return default_ticket_type
    
    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        """根據 ID 獲取活動"""
        return db.query(Event).filter(Event.id == event_id).first()
    
    @staticmethod
    def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
        """獲取活動列表"""
        # 驗證分頁參數
        skip = max(0, skip)  # 確保 skip 不是負數
        limit = max(1, min(100, limit))  # 確保 limit 在 1-100 之間
        
        return db.query(Event).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_events_by_merchant(db: Session, merchant_id: int, skip: int = 0, limit: int = 100) -> List[Event]:
        """獲取指定商戶的活動列表（支援分頁）"""
        # 驗證分頁參數
        skip = max(0, skip)  # 確保 skip 不是負數
        limit = max(1, min(100, limit))  # 確保 limit 在 1-100 之間
        
        return db.query(Event).filter(Event.merchant_id == merchant_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_event(db: Session, event_id: int, event_data: EventUpdate) -> Optional[Event]:
        """更新活動"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None
        
        update_data = event_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        db.commit()
        db.refresh(event)
        return event
    
    @staticmethod
    def create_ticket_type(db: Session, ticket_type_data: TicketTypeCreate) -> TicketType:
        """建立票種"""
        # 檢查票種配額是否會超過活動總配額
        EventService._validate_ticket_type_quota(db, ticket_type_data.event_id, ticket_type_data.quota)
        
        ticket_type = TicketType(**ticket_type_data.dict())
        db.add(ticket_type)
        db.commit()
        db.refresh(ticket_type)
        return ticket_type
    
    @staticmethod
    def _validate_ticket_type_quota(db: Session, event_id: int, new_quota: int) -> None:
        """驗證票種配額不會導致總配額超過活動限制"""
        if not new_quota or new_quota <= 0:
            return  # 無限制配額，跳過檢查
        
        # 獲取活動資訊
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event or not event.total_quota or event.total_quota <= 0:
            return  # 活動不存在或無配額限制，跳過檢查
        
        # 計算現有票種配額總和
        existing_ticket_types = db.query(TicketType).filter(TicketType.event_id == event_id).all()
        total_ticket_type_quota = sum(tt.quota for tt in existing_ticket_types if tt.quota and tt.quota > 0)
        
        # 檢查新配額是否會導致超過活動總配額
        projected_total = total_ticket_type_quota + new_quota
        if projected_total > event.total_quota:
            raise ValueError(
                f"票種配額總和將超過活動總配額。"
                f"現有票種配額總和: {total_ticket_type_quota}, "
                f"新增配額: {new_quota}, "
                f"總計: {projected_total}, "
                f"活動配額上限: {event.total_quota}"
            )
    
    @staticmethod
    def get_ticket_types_by_event(db: Session, event_id: int) -> List[TicketType]:
        """獲取活動的票種列表"""
        return db.query(TicketType).filter(TicketType.event_id == event_id).all()
    
    @staticmethod
    def get_ticket_type_by_id_and_merchant(db: Session, ticket_type_id: int, merchant_id: Optional[int] = None) -> Optional[TicketType]:
        """根據 ID 獲取票種（多租戶支援）"""
        query = db.query(TicketType).filter(TicketType.id == ticket_type_id)
        
        if merchant_id is not None:
            # 多租戶模式：透過 event 關聯確認票種屬於該商戶
            query = query.join(Event).filter(Event.merchant_id == merchant_id)
        
        return query.first()
    
    @staticmethod
    def update_ticket_type(db: Session, ticket_type_id: int, ticket_type_data: TicketTypeUpdate) -> Optional[TicketType]:
        """更新票種"""
        ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
        if not ticket_type:
            return None
        
        update_data = ticket_type_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket_type, field, value)
        
        db.commit()
        db.refresh(ticket_type)
        return ticket_type
    
    @staticmethod
    def get_offline_tickets(db: Session, event_id: int) -> List[dict]:
        """獲取活動的離線票券資料"""
        tickets = (db.query(Ticket, TicketType.name.label('ticket_type_name'))
                  .outerjoin(TicketType, Ticket.ticket_type_id == TicketType.id)
                  .filter(Ticket.event_id == event_id)
                  .all())
        
        result = []
        for ticket, ticket_type_name in tickets:
            result.append({
                "ticket_id": ticket.id,
                "ticket_code": ticket.ticket_code,
                "holder_name": ticket.holder_name,
                "ticket_type_name": ticket_type_name,
                "is_used": ticket.is_used
            })
        
        return result
    
    @staticmethod
    def delete_event(db: Session, event_id: int) -> bool:
        """刪除活動"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return False
        
        db.delete(event)
        db.commit()
        return True
    
    @staticmethod
    def delete_ticket_type_by_merchant(db: Session, ticket_type_id: int, merchant_id: Optional[int] = None) -> bool:
        """刪除票券類型（多租戶安全）"""
        query = db.query(TicketType).filter(TicketType.id == ticket_type_id)
        if merchant_id:
            # 透過 event 關聯確認票種屬於該商戶
            query = query.join(Event).filter(Event.merchant_id == merchant_id)
        ticket_type = query.first()
        if not ticket_type:
            return False
        db.delete(ticket_type)
        db.commit()
        return True
    
    @staticmethod
    def get_ticket_type_by_id(db: Session, ticket_type_id: int) -> Optional[TicketType]:
        """根據ID獲取票種"""
        return db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    
    @staticmethod
    def delete_ticket_type(db: Session, ticket_type_id: int) -> bool:
        """刪除票種"""
        ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
        if not ticket_type:
            return False
        
        # 檢查是否有相關的票券
        from models.ticket import Ticket
        existing_tickets = db.query(Ticket).filter(Ticket.ticket_type_id == ticket_type_id).count()
        if existing_tickets > 0:
            raise ValueError(f"無法刪除票種，還有 {existing_tickets} 張票券使用此票種")
        
        db.delete(ticket_type)
        db.commit()
        return True
    
    @staticmethod
    def get_event_summary(db: Session, event_id: int) -> dict:
        """獲取活動摘要"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")
        
        # 取得票種資訊
        ticket_types = db.query(TicketType).filter(TicketType.event_id == event_id).all()
        
        # 取得票券統計
        from models.ticket import Ticket
        total_tickets = db.query(Ticket).filter(Ticket.event_id == event_id).count()
        used_tickets = db.query(Ticket).filter(
            Ticket.event_id == event_id, 
            Ticket.is_used == True
        ).count()
        
        # 取得簽到統計
        from models.checkin import CheckInLog
        checkin_count = db.query(CheckInLog).join(Ticket).filter(
            Ticket.event_id == event_id
        ).count()
        
        ticket_type_summary = []
        for tt in ticket_types:
            tt_tickets = db.query(Ticket).filter(Ticket.ticket_type_id == tt.id).count()
            tt_used = db.query(Ticket).filter(
                Ticket.ticket_type_id == tt.id,
                Ticket.is_used == True
            ).count()
            
            ticket_type_summary.append({
                "id": tt.id,
                "name": tt.name,
                "quota": tt.quota,
                "issued": tt_tickets,
                "used": tt_used,
                "remaining": tt.quota - tt_tickets if tt.quota > 0 else None
            })
        
        return {
            "event": {
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "location": event.location,
                "total_quota": event.total_quota,
                "is_active": event.is_active
            },
            "statistics": {
                "total_tickets": total_tickets,
                "used_tickets": used_tickets,
                "unused_tickets": total_tickets - used_tickets,
                "checkin_count": checkin_count,
                "usage_rate": round(used_tickets / total_tickets * 100, 2) if total_tickets > 0 else 0
            },
            "ticket_types": ticket_type_summary
        }
