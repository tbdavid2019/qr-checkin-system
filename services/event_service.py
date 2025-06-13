"""
活動服務
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Event, TicketType, Ticket
from schemas.event import EventCreate, EventUpdate, TicketTypeCreate, TicketTypeUpdate

class EventService:
    
    @staticmethod
    def create_event(db: Session, event_data: EventCreate) -> Event:
        """建立活動"""
        event = Event(**event_data.dict())
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        """根據 ID 獲取活動"""
        return db.query(Event).filter(Event.id == event_id).first()
    
    @staticmethod
    def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
        """獲取活動列表"""
        return db.query(Event).offset(skip).limit(limit).all()
    
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
        ticket_type = TicketType(**ticket_type_data.dict())
        db.add(ticket_type)
        db.commit()
        db.refresh(ticket_type)
        return ticket_type
    
    @staticmethod
    def get_ticket_types_by_event(db: Session, event_id: int) -> List[TicketType]:
        """獲取活動的票種列表"""
        return db.query(TicketType).filter(TicketType.event_id == event_id).all()
    
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
