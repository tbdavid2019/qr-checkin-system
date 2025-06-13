from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from .base import Base


class TicketType(Base):
    __tablename__ = "ticket_types"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "一般票", "早鳥票", "VIP票"
    price = Column(Numeric(10, 2), nullable=True)
    quota = Column(Integer, nullable=False, default=0)  # 票種配額
    is_active = Column(Boolean, default=True)
    
    # Relationships
    event = relationship("Event", back_populates="ticket_types")
    tickets = relationship("Ticket", back_populates="ticket_type")
