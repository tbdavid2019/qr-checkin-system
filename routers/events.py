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
    TicketTypeBase, TicketTypeCreate, TicketTypeUpdate, TicketType, OfflineTicket
)
from schemas.common import APIResponse
from services.event_service import EventService
from services.staff_service import StaffService
from app.config import settings

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=List[Event])
def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
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
    merchant = Depends(require_api_key)
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
    merchant = Depends(require_api_key)
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
    merchant = Depends(require_api_key)
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
    merchant = Depends(require_api_key)
):
    """
    為活動創建票種
    
    🎫 **此為產票前必要步驟！**
    
    **使用流程**:
    1. **先執行此 API** 為活動建立票種
    2. 記錄回傳的票種 ID (ticket_type_id)
    3. 使用票種 ID 透過票券 API 產生票券：
       - `/api/tickets/` (單筆)
       - `/api/tickets/batch` (批次)
       - `/api/tickets-mgmt/` (管理版本)
       - `/api/tickets-mgmt/batch` (管理版本)
    
    **票種範例**:
    - 一般票、VIP票、早鳥票等
    - 每種票種可設定不同價格和數量
    """
    # 檢查活動是否存在並屬於該商戶
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # 在多租戶模式下檢查權限
    if settings.ENABLE_MULTI_TENANT:
        if event.merchant_id != merchant.id:
            raise HTTPException(status_code=404, detail="Event not found")
    
    # 創建包含 event_id 的完整數據
    ticket_type_create_data = TicketTypeCreate(
        event_id=event_id,
        **ticket_type_data.dict()
    )
    
    ticket_type = EventService.create_ticket_type(db, ticket_type_create_data)
    return ticket_type

@router.patch("/ticket-types/{ticket_type_id}", response_model=TicketType)
def update_ticket_type(
    ticket_type_id: int,
    ticket_type_data: TicketTypeUpdate,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """修改票種資訊（含 quota 數量）"""
    # 驗證票種是否屬於該商戶的活動
    ticket_type = EventService.get_ticket_type_by_id_and_merchant(db, ticket_type_id, merchant.id if merchant else None)
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    
    updated_ticket_type = EventService.update_ticket_type(db, ticket_type_id, ticket_type_data)
    return updated_ticket_type

@router.delete("/ticket-types/{ticket_type_id}", response_model=APIResponse)
def delete_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """刪除票券類型（多租戶安全）"""
    success = EventService.delete_ticket_type_by_merchant(db, ticket_type_id, merchant.id if merchant else None)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    return APIResponse(message="Ticket type deleted successfully")

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
