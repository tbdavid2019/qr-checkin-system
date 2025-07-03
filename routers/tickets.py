"""
租戶票券管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_merchant
from schemas.ticket import (
    TicketCreate, TicketUpdate, Ticket, BatchTicketCreate
)
from schemas.common import APIResponse
from services.ticket_service import TicketService
from models.merchant import Merchant

router = APIRouter(prefix="/api/v1/mgmt/tickets", tags=["Tenant Mgmt: Tickets"])

def _convert_ticket_model_to_schema(ticket_model) -> Ticket:
    """將 SQLAlchemy Ticket model 轉換為 Pydantic Ticket schema，並處理 uuid."""
    return Ticket(
        id=ticket_model.id,
        uuid=ticket_model.uuid,
        event_id=ticket_model.event_id,
        ticket_type_id=ticket_model.ticket_type_id,
        ticket_code=ticket_model.ticket_code,
        is_used=ticket_model.is_used,
        created_at=ticket_model.created_at,
        updated_at=ticket_model.updated_at,
        holder_name=ticket_model.holder_name,
        holder_email=ticket_model.holder_email,
        holder_phone=ticket_model.holder_phone,
        external_user_id=ticket_model.external_user_id,
        notes=ticket_model.notes,
        description=ticket_model.description
    )

@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(
    ticket_id: int, 
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """查詢票券詳細資料"""
    ticket = TicketService.get_ticket_by_id_and_merchant(db, ticket_id, merchant.id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return _convert_ticket_model_to_schema(ticket)

@router.get("", response_model=List[Ticket])
def get_tickets(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """查詢活動票券清單"""
    tickets_db = TicketService.get_tickets_by_event_and_merchant(db, event_id, merchant.id, skip, limit)
    return [_convert_ticket_model_to_schema(t) for t in tickets_db]

@router.post("", response_model=Ticket)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """創建單張票券"""
    try:
        ticket = TicketService.create_ticket_with_merchant(db, ticket_data, merchant.id)
        return _convert_ticket_model_to_schema(ticket)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch", response_model=List[Ticket])
def create_batch_tickets(
    batch_data: BatchTicketCreate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """批次產票"""
    try:
        tickets_db = TicketService.create_batch_tickets_with_merchant(db, batch_data, merchant.id)
        return [_convert_ticket_model_to_schema(t) for t in tickets_db]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{ticket_id}", response_model=Ticket)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """更新票券資訊"""
    ticket = TicketService.update_ticket_by_merchant(db, ticket_id, ticket_data, merchant.id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or no permission")
    return _convert_ticket_model_to_schema(ticket)

@router.delete("/{ticket_id}", response_model=APIResponse)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """刪除票券"""
    success = TicketService.delete_ticket_by_merchant(db, ticket_id, merchant.id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found or no permission")
    return APIResponse(success=True, message="Ticket deleted")

@router.get("/search/by-holder", response_model=List[Ticket])
def get_tickets_by_holder(
    email: Optional[str] = Query(None, description="持有人電子郵件"),
    phone: Optional[str] = Query(None, description="持有人電話"),
    external_user_id: Optional[str] = Query(None, description="外部用戶ID"),
    event_id: Optional[int] = Query(None, description="活動ID過濾"),
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant)
):
    """透過持有人資訊搜尋票券"""
    tickets_db = TicketService.search_tickets_by_holder_for_merchant(
        db=db, 
        merchant_id=merchant.id, 
        email=email, 
        phone=phone, 
        external_user_id=external_user_id,
        event_id=event_id
    )
    return [_convert_ticket_model_to_schema(t) for t in tickets_db]
