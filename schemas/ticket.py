"""
票券相關的 Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# 票券基本 schema
class TicketBase(BaseModel):
    holder_name: str
    holder_email: Optional[str] = None
    holder_phone: Optional[str] = None
    external_user_id: Optional[str] = None
    notes: Optional[str] = None
    description: Optional[str] = None  # JSON 格式的額外資訊

class TicketCreate(TicketBase):
    event_id: int
    ticket_type_id: Optional[int] = None

class TicketUpdate(BaseModel):
    holder_name: Optional[str] = None
    holder_email: Optional[str] = None
    holder_phone: Optional[str] = None
    notes: Optional[str] = None
    description: Optional[str] = None  # JSON 格式的額外資訊

class Ticket(TicketBase):
    id: int
    event_id: int
    ticket_type_id: Optional[int]
    ticket_code: str
    is_used: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# QR Code 相關
class QRTokenPayload(BaseModel):
    ticket_id: int
    event_id: int
    exp: int  # 過期時間戳

class TicketVerifyRequest(BaseModel):
    qr_token: str

class TicketVerifyResponse(BaseModel):
    valid: bool
    ticket_id: Optional[int] = None
    event_id: Optional[int] = None
    holder_name: Optional[str] = None
    ticket_type_name: Optional[str] = None
    is_used: bool = False
    message: str

# 批次產票
class BatchTicketCreate(BaseModel):
    event_id: int
    ticket_type_id: Optional[int] = None
    count: int
    holder_name_prefix: str = "票券"  # 例如: "票券001", "票券002"
    description: Optional[str] = None  # JSON 格式的額外資訊，套用到所有票券
