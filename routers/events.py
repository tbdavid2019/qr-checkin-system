"""
活動相關 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_merchant
from schemas.event import (
    EventCreate, EventUpdate, Event, EventWithTicketTypes,
    TicketTypeBase, TicketTypeCreate, TicketTypeUpdate, TicketType, OfflineTicket
)
from schemas.common import APIResponse
from services.event_service import EventService
from app.config import settings
from models.merchant import Merchant

router = APIRouter(prefix="/api/v1/mgmt/events", tags=["Tenant Mgmt: Events"])

@router.get("", response_model=List[Event])
def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """查詢活動列表（商戶專用）"""
    if settings.ENABLE_MULTI_TENANT:
        merchant_id = merchant.id
        events = EventService.get_events_by_merchant(db, merchant_id, skip, limit)
    else:
        events = EventService.get_events(db, skip, limit)
    return events

@router.get("/{event_id}", response_model=EventWithTicketTypes)
def get_event(
    event_id: int, 
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """查詢單一活動資料"""
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # 在多租戶模式下檢查權限
    if settings.ENABLE_MULTI_TENANT:
        if event.merchant_id != merchant.id:
            raise HTTPException(status_code=404, detail="Event not found")
    
    ticket_types = EventService.get_ticket_types_by_event(db, event_id)
    
    return EventWithTicketTypes(
        **event.__dict__,
        ticket_types=ticket_types
    )

@router.get("/{event_id}/ticket-types", response_model=List[TicketType])
def get_event_ticket_types(
    event_id: int, 
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """查詢活動票種與配額"""
    # 檢查活動是否存在
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # 在多租戶模式下檢查權限
    if settings.ENABLE_MULTI_TENANT:
        if event.merchant_id != merchant.id:
            raise HTTPException(status_code=404, detail="Event not found")
    
    ticket_types = EventService.get_ticket_types_by_event(db, event_id)
    return ticket_types

@router.post("", response_model=Event)
def create_event(
    event_data: EventCreate, 
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """建立活動"""
    if settings.ENABLE_MULTI_TENANT:
        merchant_id = merchant.id
        event = EventService.create_event(db, event_data, merchant_id)
    else:
        event = EventService.create_event(db, event_data)
    return event

@router.post("/{event_id}/ticket-types", response_model=TicketType)
def create_ticket_type(
    event_id: int,
    ticket_type_data: TicketTypeBase,  # 使用 Base 而不是 Create
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """
    為活動創建票種
    
    - **event_id**: 活動 ID
    - **ticket_type_data**: 票種資訊
    """
    # 檢查活動是否存在且屬於該商戶
    event = EventService.get_event_by_id(db, event_id)
    if not event or (settings.ENABLE_MULTI_TENANT and event.merchant_id != merchant.id):
        raise HTTPException(status_code=404, detail="Event not found")

    # 將 event_id 加入到 ticket_type_data 中
    ticket_type_create_data = TicketTypeCreate(**ticket_type_data.dict(), event_id=event_id)
    
    try:
        return EventService.create_ticket_type(db, ticket_type_create_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{event_id}", response_model=Event)
def update_event(
    event_id: int, 
    event_data: EventUpdate, 
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """更新活動資訊"""
    # 檢查活動是否存在且屬於該商戶
    event = EventService.get_event_by_id(db, event_id)
    if not event or (settings.ENABLE_MULTI_TENANT and event.merchant_id != merchant.id):
        raise HTTPException(status_code=404, detail="Event not found")
        
    updated_event = EventService.update_event(db, event_id, event_data)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@router.put("/ticket-types/{ticket_type_id}", response_model=TicketType)
def update_ticket_type(
    ticket_type_id: int,
    ticket_type_data: TicketTypeUpdate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """更新票種資訊"""
    # 檢查票種是否存在
    ticket_type = EventService.get_ticket_type_by_id(db, ticket_type_id)
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")

    # 檢查票種所屬的活動是否屬於該商戶
    event = EventService.get_event_by_id(db, ticket_type.event_id)
    if not event or (settings.ENABLE_MULTI_TENANT and event.merchant_id != merchant.id):
        raise HTTPException(status_code=403, detail="Permission denied")

    updated_ticket_type = EventService.update_ticket_type(db, ticket_type_id, ticket_type_data)
    if not updated_ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    return updated_ticket_type

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int, 
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """刪除活動"""
    # 檢查活動是否存在且屬於該商戶
    event = EventService.get_event_by_id(db, event_id)
    if not event or (settings.ENABLE_MULTI_TENANT and event.merchant_id != merchant.id):
        raise HTTPException(status_code=404, detail="Event not found")

    success = EventService.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete event")
    return None

@router.delete("/ticket-types/{ticket_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """刪除票種"""
    # 檢查票種是否存在
    ticket_type = EventService.get_ticket_type_by_id(db, ticket_type_id)
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")

    # 檢查票種所屬的活動是否屬於該商戶
    event = EventService.get_event_by_id(db, ticket_type.event_id)
    if not event or (settings.ENABLE_MULTI_TENANT and event.merchant_id != merchant.id):
        raise HTTPException(status_code=403, detail="Permission denied")

    success = EventService.delete_ticket_type(db, ticket_type_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete ticket type")
    return None

@router.post("/{event_id}/offline-tickets", response_model=TicketType, deprecated=True)
def create_offline_ticket_type(
    event_id: int,
    offline_ticket_data: OfflineTicket,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """
    (已棄用) 建立線下票種 (例如: 現場票)
    請改用 POST /ticket-types
    """
    # 檢查活動是否存在且屬於該商戶
    event = EventService.get_event_by_id(db, event_id)
    if not event or (settings.ENABLE_MULTI_TENANT and event.merchant_id != merchant.id):
        raise HTTPException(status_code=404, detail="Event not found")

    ticket_type_data = TicketTypeCreate(
        event_id=event_id,
        name=offline_ticket_data.name,
        price=offline_ticket_data.price,
        quantity=offline_ticket_data.quantity,
        is_online=False
    )
    return EventService.create_ticket_type(db, ticket_type_data)

@router.get("/{event_id}/summary", response_model=dict)
def get_event_summary(
    event_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """獲取活動摘要，包括票券銷售與核銷統計"""
    # 檢查活動是否存在且屬於該商戶
    event = EventService.get_event_by_id(db, event_id)
    if not event or (settings.ENABLE_MULTI_TENANT and event.merchant_id != merchant.id):
        raise HTTPException(status_code=404, detail="Event not found")
        
    summary = EventService.get_event_summary(db, event_id)
    return summary
