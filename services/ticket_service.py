"""
Ticket Service
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.ticket import Ticket
from models.event import Event  
from models.ticket_type import TicketType
from schemas.ticket import TicketCreate, TicketUpdate, BatchTicketCreate
from utils.qr_code import generate_ticket_code

class TicketService:
    @staticmethod
    def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
        """Create a single ticket"""
        # Check if event exists
        event = db.query(Event).filter(Event.id == ticket_data.event_id).first()
        if not event:
            raise ValueError("Event not found")
        
        # Check event total quota limit
        if event.total_quota is not None and event.total_quota > 0:
            current_total_tickets = db.query(Ticket).filter(Ticket.event_id == ticket_data.event_id).count()
            if current_total_tickets >= event.total_quota:
                raise ValueError(f"Event total quota exceeded. Event quota ({event.total_quota}) is full.")
        
        # Validate ticket type belongs to event and check ticket type quota
        if ticket_data.ticket_type_id:
            ticket_type = db.query(TicketType).filter(
                and_(TicketType.id == ticket_data.ticket_type_id, TicketType.event_id == ticket_data.event_id)
            ).first()
            if not ticket_type:
                raise ValueError("Ticket type not found or does not belong to the event")

            # Check ticket type quota
            if ticket_type.quota is not None and ticket_type.quota > 0:
                current_ticket_count = db.query(Ticket).filter(Ticket.ticket_type_id == ticket_data.ticket_type_id).count()
                if current_ticket_count >= ticket_type.quota:
                    raise ValueError(f"Ticket type quota exceeded. Quota ({ticket_type.quota}) is full.")
        
        # Generate unique ticket code
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
        """Create batch tickets"""
        # Check if event exists
        event = db.query(Event).filter(Event.id == batch_data.event_id).first()
        if not event:
            raise ValueError("Event not found")
        
        # Check event total quota limit
        if event.total_quota is not None and event.total_quota > 0:
            current_total_tickets = db.query(Ticket).filter(Ticket.event_id == batch_data.event_id).count()
            if current_total_tickets + batch_data.count > event.total_quota:
                remaining_quota = event.total_quota - current_total_tickets
                raise ValueError(f"Event total quota exceeded. Requested {batch_data.count} tickets, but only {remaining_quota} remaining.")
        
        # Check ticket type quota
        if batch_data.ticket_type_id:
            ticket_type = db.query(TicketType).filter(
                and_(TicketType.id == batch_data.ticket_type_id, TicketType.event_id == batch_data.event_id)
            ).first()
            if not ticket_type:
                raise ValueError("Ticket type not found or does not belong to the event")
                
            if ticket_type.quota is not None and ticket_type.quota > 0:
                current_ticket_count = db.query(Ticket).filter(Ticket.ticket_type_id == batch_data.ticket_type_id).count()
                if current_ticket_count + batch_data.count > ticket_type.quota:
                    remaining_quota = ticket_type.quota - current_ticket_count
                    raise ValueError(f"Ticket type quota exceeded. Requested {batch_data.count} tickets, but only {remaining_quota} remaining.")
        
        tickets = []
        for i in range(batch_data.count):
            # Generate unique ticket code
            while True:
                ticket_code = generate_ticket_code()
                if not db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first():
                    break
            
            ticket = Ticket(
                event_id=batch_data.event_id,
                ticket_type_id=batch_data.ticket_type_id,
                ticket_code=ticket_code,
                holder_name=f"{batch_data.holder_name_prefix}{i+1:03d}",
                description=batch_data.description
            )
            tickets.append(ticket)
            db.add(ticket)
        
        db.commit()
        for ticket in tickets:
            db.refresh(ticket)
        return tickets
        
    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Ticket:
        """Get ticket by ID"""
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    @staticmethod
    def get_ticket_by_id_and_merchant(db: Session, ticket_id: int, merchant_id: int) -> Ticket:
        """Get ticket by ID and merchant_id (multi-tenant safe)"""
        return db.query(Ticket).join(Event).filter(
            and_(Ticket.id == ticket_id, Event.merchant_id == merchant_id)
        ).first()
    
    @staticmethod
    def get_ticket_by_uuid(db: Session, ticket_uuid: int) -> Ticket:
        """Get ticket by UUID (now Snowflake ID)"""
        return db.query(Ticket).filter(Ticket.uuid == ticket_uuid).first()
    
    @staticmethod
    def get_ticket_by_code(db: Session, ticket_code: str) -> Ticket:
        """Get ticket by ticket code"""
        return db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first()
    
    @staticmethod 
    def get_tickets_by_event(db: Session, event_id: int) -> List[Ticket]:
        """Get all tickets for an event"""
        return db.query(Ticket).filter(Ticket.event_id == event_id).all()
    
    @staticmethod
    def get_tickets_by_event_and_merchant(db: Session, event_id: int, merchant_id: int = None, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Query tickets by event_id and merchant_id (multi-tenant safe)"""
        # Validate pagination parameters
        skip = max(0, skip)  # Ensure skip is not negative
        limit = max(1, min(100, limit))  # Ensure limit is between 1-100
        
        query = db.query(Ticket).filter(Ticket.event_id == event_id)
        if merchant_id:
            query = query.join(Event).filter(Event.merchant_id == merchant_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> bool:
        """Delete ticket"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return False
        
        db.delete(ticket)
        db.commit()
        return True
    
    @staticmethod
    def update_ticket(db: Session, ticket_id: int, ticket_data: TicketUpdate) -> Ticket:
        """Update ticket information"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise ValueError("Ticket not found")
        
        for field, value in ticket_data.dict(exclude_unset=True).items():
            setattr(ticket, field, value)
        
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def mark_ticket_used(db: Session, ticket_id: int) -> Ticket:
        """Mark ticket as used"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.is_used = True
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def create_batch_tickets_with_merchant(db: Session, batch_data: BatchTicketCreate, merchant_id: int = None) -> List[Ticket]:
        """Create batch tickets (multi-tenant safe, validates event/ticket_type belongs to merchant)"""
        # Validate event and ticket_type belong to merchant
        event_query = db.query(Event).filter(Event.id == batch_data.event_id)
        ticket_type_query = db.query(TicketType).filter(TicketType.id == batch_data.ticket_type_id)
        if merchant_id:
            event_query = event_query.filter(Event.merchant_id == merchant_id)
            # Confirm ticket type belongs to merchant through event association
            ticket_type_query = ticket_type_query.join(Event).filter(Event.merchant_id == merchant_id)
        
        event = event_query.first()
        ticket_type = ticket_type_query.first()

        if not event or not ticket_type:
            raise ValueError("Event or TicketType does not belong to this merchant or does not exist")

        # Check event total quota limit
        if event.total_quota is not None and event.total_quota > 0:
            current_total_tickets = db.query(Ticket).filter(Ticket.event_id == batch_data.event_id).count()
            if current_total_tickets + batch_data.count > event.total_quota:
                remaining_quota = event.total_quota - current_total_tickets
                raise ValueError(f"Event total quota exceeded. Requested {batch_data.count} tickets, but only {remaining_quota} remaining.")

        # Check ticket type quota
        if ticket_type.quota is not None and ticket_type.quota > 0:
            current_ticket_count = db.query(Ticket).filter(Ticket.ticket_type_id == batch_data.ticket_type_id).count()
            if current_ticket_count + batch_data.count > ticket_type.quota:
                remaining_quota = ticket_type.quota - current_ticket_count
                raise ValueError(f"Ticket type quota exceeded. Requested {batch_data.count} tickets, but only {remaining_quota} remaining.")
        
        tickets = []
        for i in range(batch_data.count):
            # Generate unique ticket code
            while True:
                ticket_code = generate_ticket_code()
                if not db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first():
                    break
            ticket = Ticket(
                event_id=batch_data.event_id,
                ticket_type_id=batch_data.ticket_type_id,
                ticket_code=ticket_code,
                holder_name=f"{batch_data.holder_name_prefix}{i+1:03d}",
                description=batch_data.description  # Add description support
            )
            tickets.append(ticket)
            db.add(ticket)
        db.commit()
        for ticket in tickets:
            db.refresh(ticket)
        return tickets

    @staticmethod
    def delete_ticket_with_merchant(db: Session, ticket_id: int, merchant_id: int = None) -> bool:
        """Delete ticket (multi-tenant safe)"""
        if merchant_id:
            ticket = db.query(Ticket).join(Event).filter(
                and_(Ticket.id == ticket_id, Event.merchant_id == merchant_id)
            ).first()
        else:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            return False
        
        db.delete(ticket)
        db.commit()
        return True

    @staticmethod
    def update_ticket_with_merchant(db: Session, ticket_id: int, ticket_data: TicketUpdate, merchant_id: int = None) -> Ticket:
        """Update ticket information (multi-tenant safe)"""
        if merchant_id:
            ticket = db.query(Ticket).join(Event).filter(
                and_(Ticket.id == ticket_id, Event.merchant_id == merchant_id)
            ).first()
        else:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            raise ValueError("Ticket not found or no permission")
        
        for field, value in ticket_data.dict(exclude_unset=True).items():
            setattr(ticket, field, value)
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def create_ticket_with_merchant(db: Session, ticket_data: TicketCreate, merchant_id: int = None) -> Ticket:
        """Create single ticket (multi-tenant safe)"""
        # Validate event belongs to merchant and get event info
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

        # Check event total quota limit
        if event.total_quota is not None and event.total_quota > 0:
            current_total_tickets = db.query(Ticket).filter(Ticket.event_id == ticket_data.event_id).count()
            if current_total_tickets >= event.total_quota:
                raise ValueError(f"Event total quota exceeded. Event quota ({event.total_quota}) is full.")
        
        # Validate ticket type belongs to event and check ticket type quota  
        if ticket_data.ticket_type_id:
            if merchant_id:
                # Multi-tenant filter
                ticket_type = db.query(TicketType).join(Event).filter(
                    and_(
                        TicketType.id == ticket_data.ticket_type_id, 
                        TicketType.event_id == ticket_data.event_id,
                        Event.merchant_id == merchant_id
                    )
                ).first()
            else:
                ticket_type = db.query(TicketType).filter(
                    and_(TicketType.id == ticket_data.ticket_type_id, TicketType.event_id == ticket_data.event_id)
                ).first()
            
            if not ticket_type:
                raise ValueError("Ticket type not found or does not belong to the event")

            # Check ticket type quota
            if ticket_type.quota is not None and ticket_type.quota > 0:
                current_ticket_count = db.query(Ticket).filter(Ticket.ticket_type_id == ticket_data.ticket_type_id).count()
                if current_ticket_count >= ticket_type.quota:
                    raise ValueError(f"Ticket type quota exceeded. Quota ({ticket_type.quota}) is full.")
        
        # Generate unique ticket code
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
    def search_tickets_by_holder_for_merchant(
        db: Session, 
        merchant_id: int, 
        email: Optional[str] = None,
        phone: Optional[str] = None,
        external_user_id: Optional[str] = None,
        event_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> List[Ticket]:
        """Search tickets by holder information (multi-tenant support)"""
        skip = max(0, skip)
        limit = max(1, min(100, limit))
        
        query = db.query(Ticket).join(Event).filter(Event.merchant_id == merchant_id)
        
        # Add search filters based on provided parameters
        if email:
            query = query.filter(Ticket.holder_email.ilike(f"%{email}%"))
        if phone:
            query = query.filter(Ticket.holder_phone.ilike(f"%{phone}%"))
        if external_user_id:
            query = query.filter(Ticket.external_user_id.ilike(f"%{external_user_id}%"))
        if event_id:
            query = query.filter(Ticket.event_id == event_id)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def search_tickets_by_holder(db: Session, holder_name: str, skip: int = 0, limit: int = 50) -> List[Ticket]:
        """Search tickets by holder information (no merchant consideration)"""
        skip = max(0, skip)
        limit = max(1, min(100, limit))
        
        query = db.query(Ticket).filter(Ticket.holder_name.ilike(f"%{holder_name}%"))
        return query.offset(skip).limit(limit).all()
