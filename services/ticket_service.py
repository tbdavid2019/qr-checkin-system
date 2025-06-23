"""
票券服務
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, cast
from sqlalchemy.dialects.postgresql import UUID
from models import Ticket, Event, TicketType
from schemas.ticket import TicketCreate, TicketUpdate, BatchTicketCreate
from utils.security import generate_ticket_code
import uuid

class TicketService:
    
    @staticmethod
    def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
        """建立單張票券"""
        # 生成唯一票券代碼
        while True:
            ticket_code = generate_ticket_code()
            if not db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first():
                break
        
        ticket = Ticket(
            **ticket_data.dict(),
            ticket_code=ticket_code
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def create_batch_tickets(db: Session, batch_data: BatchTicketCreate) -> List[Ticket]:
        """批次建立票券"""
        tickets = []
        for i in range(batch_data.count):
            # 生成唯一票券代碼
            while True:
                ticket_code = generate_ticket_code()
                if not db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first():
                    break
            
            ticket = Ticket(
                event_id=batch_data.event_id,
                ticket_type_id=batch_data.ticket_type_id,
                ticket_code=ticket_code,
                holder_name=f"{batch_data.holder_name_prefix}{i+1:03d}"
            )
            tickets.append(ticket)
            db.add(ticket)
        
        db.commit()
        for ticket in tickets:
            db.refresh(ticket)
        return tickets
    
    @staticmethod
    def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
        """根據 ID 獲取票券"""
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    @staticmethod
    def get_ticket_by_id_and_merchant(db: Session, ticket_id: int, merchant_id: int = None) -> Optional[Ticket]:
        """根據 ID 與 merchant_id 獲取票券（多租戶安全）"""
        query = db.query(Ticket).filter(Ticket.id == ticket_id)
        if merchant_id:
            query = query.join(Event).filter(Event.merchant_id == merchant_id)
        return query.first()

    @staticmethod
    def get_ticket_by_uuid(db: Session, ticket_uuid: str) -> Optional[Ticket]:
        """根據 UUID 獲取票券"""
        try:
            uuid_obj = uuid.UUID(ticket_uuid)
        except ValueError:
            return None
        return db.query(Ticket).filter(Ticket.uuid == uuid_obj).first()

    @staticmethod
    def get_ticket_by_code(db: Session, ticket_code: str) -> Optional[Ticket]:
        """根據票券代碼獲取票券"""
        return db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first()
    
    @staticmethod
    def get_tickets_by_event(db: Session, event_id: int, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """獲取活動的所有票券"""
        return db.query(Ticket).filter(Ticket.event_id == event_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_tickets_by_event_and_merchant(db: Session, event_id: int, merchant_id: int = None, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """根據 event_id 與 merchant_id 查詢票券（多租戶安全）"""
        query = db.query(Ticket).filter(Ticket.event_id == event_id)
        if merchant_id:
            query = query.join(Event).filter(Event.merchant_id == merchant_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> bool:
        """刪除票券"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return False
        
        db.delete(ticket)
        db.commit()
        return True
    
    @staticmethod
    def update_ticket(db: Session, ticket_id: int, ticket_data: TicketUpdate) -> Optional[Ticket]:
        """更新票券資訊"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None
        
        update_data = ticket_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)
        
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def mark_ticket_used(db: Session, ticket_id: int) -> Optional[Ticket]:
        """標記票券為已使用"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.is_used = True
            db.commit()
            db.refresh(ticket)
        return ticket
    
    @staticmethod
    def create_batch_tickets_with_merchant(db: Session, batch_data: BatchTicketCreate, merchant_id: int = None) -> List[Ticket]:
        """批次建立票券（多租戶安全，驗證 event/ticket_type 屬於 merchant）"""
        # 驗證 event 與 ticket_type 是否屬於 merchant
        event_query = db.query(Event).filter(Event.id == batch_data.event_id)
        ticket_type_query = db.query(TicketType).filter(TicketType.id == batch_data.ticket_type_id)
        if merchant_id:
            event_query = event_query.filter(Event.merchant_id == merchant_id)
            # 透過 event 關聯確認票種屬於該商戶
            ticket_type_query = ticket_type_query.join(Event).filter(Event.merchant_id == merchant_id)
        
        event = event_query.first()
        ticket_type = ticket_type_query.first()

        if not event or not ticket_type:
            raise ValueError("Event 或 TicketType 不屬於此商戶或不存在")

        # 檢查活動總配額限制
        if event.total_quota is not None and event.total_quota > 0:
            current_total_tickets = db.query(Ticket).filter(Ticket.event_id == batch_data.event_id).count()
            if current_total_tickets + batch_data.count > event.total_quota:
                remaining_quota = event.total_quota - current_total_tickets
                raise ValueError(f"超出活動總配額。請求建立 {batch_data.count} 張，但剩餘配額僅為 {remaining_quota} 張。")

        # 檢查票種配額
        if ticket_type.quota is not None and ticket_type.quota > 0:
            current_ticket_count = db.query(Ticket).filter(Ticket.ticket_type_id == batch_data.ticket_type_id).count()
            if current_ticket_count + batch_data.count > ticket_type.quota:
                remaining_quota = ticket_type.quota - current_ticket_count
                raise ValueError(f"超出票種配額。請求建立 {batch_data.count} 張，但剩餘配額僅為 {remaining_quota} 張。")
        
        tickets = []
        for i in range(batch_data.count):
            # 生成唯一票券代碼
            while True:
                ticket_code = generate_ticket_code()
                if not db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first():
                    break
            ticket = Ticket(
                event_id=batch_data.event_id,
                ticket_type_id=batch_data.ticket_type_id,
                ticket_code=ticket_code,
                holder_name=f"{batch_data.holder_name_prefix}{i+1:03d}",
                description=batch_data.description  # 添加 description 支援
            )
            tickets.append(ticket)
            db.add(ticket)
        db.commit()
        for ticket in tickets:
            db.refresh(ticket)
        return tickets
    
    @staticmethod
    def delete_ticket_by_merchant(db: Session, ticket_id: int, merchant_id: int = None) -> bool:
        """刪除票券（多租戶安全）"""
        query = db.query(Ticket).filter(Ticket.id == ticket_id)
        if merchant_id:
            query = query.join(Event).filter(Event.merchant_id == merchant_id)
        ticket = query.first()
        if not ticket:
            return False
        db.delete(ticket)
        db.commit()
        return True

    @staticmethod
    def update_ticket_by_merchant(db: Session, ticket_id: int, ticket_data: TicketUpdate, merchant_id: int = None) -> Optional[Ticket]:
        """多租戶安全地更新票券資訊"""
        query = db.query(Ticket).filter(Ticket.id == ticket_id)
        if merchant_id:
            query = query.join(Event).filter(Event.merchant_id == merchant_id)
        ticket = query.first()
        if not ticket:
            return None
        update_data = ticket_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def create_ticket_with_merchant(db: Session, ticket_data: TicketCreate, merchant_id: int = None) -> Ticket:
        """多租戶安全地建立單張票券"""
        # 驗證活動屬於該商戶並獲取活動資訊
        if merchant_id:
            event = db.query(Event).filter(
                and_(Event.id == ticket_data.event_id, Event.merchant_id == merchant_id)
            ).first()
            if not event:
                raise ValueError("Event not found or no permission")
        else:
            event = db.query(Event).filter(Event.id == ticket_data.event_id).first()
            if not event:
                raise ValueError("Event not found")
        
        # 檢查活動總配額限制
        if event.total_quota is not None and event.total_quota > 0:
            current_total_tickets = db.query(Ticket).filter(Ticket.event_id == ticket_data.event_id).count()
            if current_total_tickets >= event.total_quota:
                raise ValueError(f"超出活動總配額。活動配額 ({event.total_quota}) 已滿。")
        
        # 驗證票種屬於該活動並檢查票種配額
        if ticket_data.ticket_type_id:
            ticket_type = db.query(TicketType).filter(
                and_(TicketType.id == ticket_data.ticket_type_id, TicketType.event_id == ticket_data.event_id)
            ).first()
            if not ticket_type:
                raise ValueError("Ticket type not found or does not belong to the event")

            # 檢查票種配額
            if ticket_type.quota is not None and ticket_type.quota > 0:
                current_ticket_count = db.query(Ticket).filter(Ticket.ticket_type_id == ticket_data.ticket_type_id).count()
                if current_ticket_count >= ticket_type.quota:
                    raise ValueError(f"超出票種配額。配額 ({ticket_type.quota}) 已滿。")

        # 生成唯一票券代碼
        while True:
            ticket_code = generate_ticket_code()
            if not db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first():
                break
        
        ticket = Ticket(
            **ticket_data.dict(),
            ticket_code=ticket_code
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def get_tickets_by_holder_info(
        db: Session, 
        merchant_id: int,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        external_user_id: Optional[str] = None,
        event_id: Optional[int] = None
    ) -> List[Ticket]:
        """根據持有人資訊查詢票券"""
        query = db.query(Ticket).join(TicketType).join(Event)
        
        # 多租戶過濾
        query = query.filter(Event.merchant_id == merchant_id)
        
        # 建立持有人條件
        holder_conditions = []
        if email:
            holder_conditions.append(Ticket.holder_email == email)
        if phone:
            holder_conditions.append(Ticket.holder_phone == phone)
        if external_user_id:
            holder_conditions.append(Ticket.external_user_id == external_user_id)
        
        # 使用 OR 條件連接持有人查詢條件
        if holder_conditions:
            query = query.filter(or_(*holder_conditions))
        
        # 額外的活動過濾
        if event_id:
            query = query.filter(Ticket.event_id == event_id)
        
        return query.all()
