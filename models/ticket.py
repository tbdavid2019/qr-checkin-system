from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=True)
    ticket_code = Column(String(50), unique=True, nullable=False, index=True)
    holder_name = Column(String(100), nullable=False)
    holder_email = Column(String(100), nullable=True)
    holder_phone = Column(String(20), nullable=True)
    external_user_id = Column(String(100), nullable=True, index=True)  # LINE ID, FB ID 等
    notes = Column(Text, nullable=True)
    description = Column(Text, nullable=True)  # JSON 格式的額外資訊（座位、席次等）
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    checkin_logs = relationship("CheckInLog", back_populates="ticket")
