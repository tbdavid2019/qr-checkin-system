from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class CheckInLog(Base):
    __tablename__ = "checkin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)  # 掃描員 ID
    checkin_time = Column(DateTime, default=func.now())
    ip_address = Column(String(45), nullable=True)  # 支援 IPv6
    user_agent = Column(String(500), nullable=True)
    is_revoked = Column(Boolean, default=False)  # 是否已撤銷
    revoked_by = Column(Integer, ForeignKey("staff.id"), nullable=True)  # 撤銷者
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="checkin_logs")
    staff = relationship("Staff", foreign_keys=[staff_id])
    revoked_by_staff = relationship("Staff", foreign_keys=[revoked_by])
