from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class StaffEvent(Base):
    """員工與活動的關聯表，定義員工可以掃描哪些活動"""
    __tablename__ = "staff_events"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    can_checkin = Column(Boolean, default=True)  # 是否可以進行簽到
    can_revoke = Column(Boolean, default=False)  # 是否可以撤銷簽到
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    staff = relationship("Staff", back_populates="staff_events")
    event = relationship("Event", back_populates="staff_events")
