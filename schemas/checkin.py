"""
簽到相關的 Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CheckInRequest(BaseModel):
    qr_token: str
    event_id: int

class CheckInResponse(BaseModel):
    success: bool
    ticket_id: Optional[int] = None
    holder_name: Optional[str] = None
    checkin_time: Optional[datetime] = None
    message: str

class CheckInRevoke(BaseModel):
    checkin_log_id: int
    reason: Optional[str] = None

class CheckInLog(BaseModel):
    id: int
    ticket_id: int
    staff_id: Optional[int]
    checkin_time: datetime
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CheckInLogDetail(CheckInLog):
    ticket: dict  # 包含票券資訊
    staff: Optional[dict] = None  # 包含員工資訊

# 離線同步相關
class OfflineCheckIn(BaseModel):
    ticket_id: int
    event_id: int
    checkin_time: datetime
    client_timestamp: str  # 客戶端時間戳

class OfflineCheckInSync(BaseModel):
    event_id: int
    checkins: list[OfflineCheckIn]
