"""
活動相關的 Pydantic schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    total_quota: Optional[int] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    total_quota: Optional[int] = None
    is_active: Optional[bool] = None

class Event(EventBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 票種相關
class TicketTypeBase(BaseModel):
    name: str
    price: Optional[float] = None
    quota: int = 0

class TicketTypeCreate(TicketTypeBase):
    event_id: int

class TicketTypeUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quota: Optional[int] = None
    is_active: Optional[bool] = None

class TicketType(TicketTypeBase):
    id: int
    event_id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class EventWithTicketTypes(Event):
    ticket_types: List[TicketType] = []

# 離線票券資料
class OfflineTicket(BaseModel):
    ticket_id: int
    ticket_code: str
    holder_name: str
    ticket_type_name: Optional[str]
    is_used: bool
