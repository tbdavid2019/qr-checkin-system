"""
票券服務
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Ticket, Event, TicketType
from schemas.ticket import TicketCreate, TicketUpdate, BatchTicketCreate
from utils.security import generate_ticket_code

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
    def get_ticket_by_code(db: Session, ticket_code: str) -> Optional[Ticket]:
        """根據票券代碼獲取票券"""
        return db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first()
    
    @staticmethod
    def get_tickets_by_event(db: Session, event_id: int, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """獲取活動的所有票券"""
        return db.query(Ticket).filter(Ticket.event_id == event_id).offset(skip).limit(limit).all()
    
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
