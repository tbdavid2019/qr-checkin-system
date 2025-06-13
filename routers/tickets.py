"""
票券相關 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff, require_api_key
from schemas.ticket import (
    TicketCreate, TicketUpdate, Ticket, BatchTicketCreate,
    TicketVerifyRequest, TicketVerifyResponse
)
from schemas.common import APIResponse
from services.ticket_service import TicketService
from services.staff_service import StaffService
from utils.auth import create_qr_token, verify_qr_token
from utils.qr_code import generate_qr_code, generate_ticket_qr_url
from models import Staff

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

@router.get("/{ticket_id}/qrcode")
def get_ticket_qr_code(
    ticket_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """產生票券 QR code（使用者前端）"""
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # 建立 QR token
    qr_token = create_qr_token(ticket.id, ticket.event_id)
    
    # 生成 QR Code URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    qr_url = generate_ticket_qr_url(base_url, qr_token)
    
    # 生成 QR Code 圖片
    qr_image = generate_qr_code(qr_url)
    
    return {
        "ticket_id": ticket.id,
        "qr_token": qr_token,
        "qr_url": qr_url,
        "qr_image": qr_image,
        "holder_name": ticket.holder_name
    }

@router.post("/verify", response_model=TicketVerifyResponse, dependencies=[Depends(require_api_key)])
def verify_ticket(verify_request: TicketVerifyRequest, db: Session = Depends(get_db)):
    """驗證 QR Token（不核銷）"""
    payload = verify_qr_token(verify_request.qr_token)
    if not payload:
        return TicketVerifyResponse(
            valid=False,
            message="Invalid or expired QR token"
        )
    
    ticket_id = payload.get("ticket_id")
    event_id = payload.get("event_id")
    
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        return TicketVerifyResponse(
            valid=False,
            message="Ticket not found"
        )
    
    if ticket.event_id != event_id:
        return TicketVerifyResponse(
            valid=False,
            message="Event mismatch"
        )
    
    # 獲取票種名稱
    ticket_type_name = None
    if ticket.ticket_type:
        ticket_type_name = ticket.ticket_type.name
    
    return TicketVerifyResponse(
        valid=True,
        ticket_id=ticket.id,
        event_id=ticket.event_id,
        holder_name=ticket.holder_name,
        ticket_type_name=ticket_type_name,
        is_used=ticket.is_used,
        message="Valid ticket"
    )

@router.get("/{ticket_id}", response_model=Ticket, dependencies=[Depends(require_api_key)])
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """查詢票券詳細資料"""
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("", response_model=List[Ticket], dependencies=[Depends(require_api_key)])
def get_tickets(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """查詢活動票券清單"""
    tickets = TicketService.get_tickets_by_event(db, event_id, skip, limit)
    return tickets

@router.post("/batch", response_model=List[Ticket], dependencies=[Depends(require_api_key)])
def create_batch_tickets(
    batch_data: BatchTicketCreate,
    db: Session = Depends(get_db)
):
    """批次產票（指定票種與數量）"""
    tickets = TicketService.create_batch_tickets(db, batch_data)
    return tickets
