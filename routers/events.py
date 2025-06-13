"""
活動相關 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff, require_api_key
from schemas.event import (
    EventCreate, EventUpdate, Event, EventWithTicketTypes,
    TicketTypeCreate, TicketTypeUpdate, TicketType, OfflineTicket
)
from schemas.common import APIResponse
from services.event_service import EventService
from services.staff_service import StaffService

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=List[Event], dependencies=[Depends(require_api_key)])
def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """查詢活動列表（平台後台）"""
    events = EventService.get_events(db, skip, limit)
    return events

@router.get("/{event_id}", response_model=EventWithTicketTypes, dependencies=[Depends(require_api_key)])
def get_event(event_id: int, db: Session = Depends(get_db)):
    """查詢單一活動資料"""
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    ticket_types = EventService.get_ticket_types_by_event(db, event_id)
    
    return EventWithTicketTypes(
        **event.__dict__,
        ticket_types=ticket_types
    )

@router.get("/{event_id}/ticket-types", response_model=List[TicketType], dependencies=[Depends(require_api_key)])
def get_event_ticket_types(event_id: int, db: Session = Depends(get_db)):
    """查詢活動票種與配額"""
    # 檢查活動是否存在
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    ticket_types = EventService.get_ticket_types_by_event(db, event_id)
    return ticket_types

@router.post("", response_model=Event, dependencies=[Depends(require_api_key)])
def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    """建立活動"""
    event = EventService.create_event(db, event_data)
    return event

@router.patch("/ticket-types/{ticket_type_id}", response_model=TicketType, dependencies=[Depends(require_api_key)])
def update_ticket_type(
    ticket_type_id: int,
    ticket_type_data: TicketTypeUpdate,
    db: Session = Depends(get_db)
):
    """修改票種資訊（含 quota 數量）"""
    ticket_type = EventService.update_ticket_type(db, ticket_type_id, ticket_type_data)
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    return ticket_type

@router.get("/{event_id}/offline-tickets", response_model=List[OfflineTicket], dependencies=[Depends(require_api_key)])
def get_offline_tickets(
    event_id: int,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """批次下載活動票券資料"""
    # 檢查員工是否有該活動的存取權限
    if not StaffService.can_access_event(db, current_staff.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this event"
        )
    
    # 檢查活動是否存在
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    offline_tickets = EventService.get_offline_tickets(db, event_id)
    
    return [
        OfflineTicket(
            ticket_id=ticket["ticket_id"],
            ticket_code=ticket["ticket_code"],
            holder_name=ticket["holder_name"],
            ticket_type_name=ticket["ticket_type_name"],
            is_used=ticket["is_used"]
        )
        for ticket in offline_tickets
    ]

@router.get("/{event_id}/statistics", response_model=dict, dependencies=[Depends(require_api_key)])
def get_event_statistics(
    event_id: int,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """查詢活動統計資訊"""
    # 檢查員工是否有該活動的存取權限
    if not StaffService.can_access_event(db, current_staff.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this event"
        )
    
    # 檢查活動是否存在
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    from services.export_service import ExportService
    statistics = ExportService.get_event_statistics(db, event_id)
    
    return statistics

@router.get("/{event_id}/export/checkin-logs", dependencies=[Depends(require_api_key)])
def export_checkin_logs(
    event_id: int,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """導出簽到記錄為CSV"""
    # 檢查員工是否有該活動的存取權限
    if not StaffService.can_access_event(db, current_staff.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this event"
        )
    
    # 檢查活動是否存在
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    from services.export_service import ExportService
    from fastapi.responses import Response
    
    csv_content = ExportService.export_checkin_logs_csv(db, event_id)
    
    # 創建文件名
    filename = f"checkin_logs_{event.name}_{event_id}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{event_id}/export/tickets", dependencies=[Depends(require_api_key)])
def export_tickets(
    event_id: int,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """導出票券清單為CSV"""
    # 檢查員工是否有該活動的存取權限
    if not StaffService.can_access_event(db, current_staff.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this event"
        )
    
    # 檢查活動是否存在
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    from services.export_service import ExportService
    from fastapi.responses import Response
    
    csv_content = ExportService.export_tickets_csv(db, event_id)
    
    # 創建文件名
    filename = f"tickets_{event.name}_{event_id}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
