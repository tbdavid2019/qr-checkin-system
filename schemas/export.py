"""
導出相關的 Pydantic schemas
"""
from typing import List, Optional
from pydantic import BaseModel

class EventStatistics(BaseModel):
    total_tickets: int
    used_tickets: int
    unused_tickets: int
    checkin_count: int
    revoked_count: int
    usage_rate: float
    ticket_types: List[dict]

class ExportFormat(BaseModel):
    format: str = "csv"  # csv, json, xlsx
    
class TicketTypeStats(BaseModel):
    name: str
    price: float
    quota: int
    sold_count: int
    used_count: int
    available_count: int
