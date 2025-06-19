"""
簡化版票券 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from schemas.ticket import TicketVerifyRequest, TicketVerifyResponse, TicketCreate, TicketUpdate, Ticket, BatchTicketCreate
from schemas.common import APIResponse
from services.ticket_service import TicketService
from app.dependencies import require_api_key
from utils.auth import create_qr_token, verify_qr_token
from utils.qr_code import generate_qr_code, generate_ticket_qr_url

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
        "ticket_code": ticket.ticket_code,
        "qr_token": qr_token,
        "qr_url": qr_url,
        "qr_image": qr_image,
        "holder_name": ticket.holder_name,
        "event_id": ticket.event_id
    }

@router.post("/verify", response_model=TicketVerifyResponse)
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

@router.post("", response_model=Ticket)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """
    創建單張票券（多租戶安全）
    
    ⚠️ **重要提醒**: 產票前請確保已建立票種！
    
    **流程說明**:
    1. 先使用 `/api/events/{event_id}/ticket-types/` 建立票種
    2. 記錄票種 ID (ticket_type_id)
    3. 使用此 API 產生單張票券
    
    **description 欄位範例**:
    ```json
    {
      "seat": "A-01",
      "zone": "VIP",
      "entrance": "Gate A"
    }
    ```
    """
    try:
        ticket = TicketService.create_ticket_with_merchant(db, ticket_data, merchant.id if merchant else None)
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/batch", response_model=list[Ticket])
def create_batch_tickets(
    batch_data: BatchTicketCreate,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """
    批次產票（多租戶安全）
    
    ⚠️ **重要提醒**: 產票前請確保已建立票種！
    
    **流程說明**:
    1. 先使用 `/api/events/{event_id}/ticket-types/` 建立票種
    2. 記錄票種 ID (ticket_type_id)  
    3. 使用此 API 批次產生票券
    
    **description 欄位範例**:
    ```json
    {
      "seat": "A-01",
      "zone": "VIP", 
      "entrance": "Gate A",
      "meal": "vegetarian"
    }
    ```
    """
    try:
        tickets = TicketService.create_batch_tickets_with_merchant(db, batch_data, merchant.id if merchant else None)
        return tickets
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(
    ticket_id: int, 
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """
    查詢單張票券詳細資料
    
    返回票券的完整資訊，包括：
    - 基本資訊：holder_name, holder_email, holder_phone
    - 外部資訊：external_user_id, notes, description
    - 票種資訊：ticket_type_id 對應的票種詳情
    - 狀態資訊：is_used, created_at 等
    """
    ticket = TicketService.get_ticket_by_id_and_merchant(db, ticket_id, merchant.id if merchant else None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("", response_model=list[Ticket])
def get_tickets(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """
    查詢活動票券清單（多租戶安全）
    
    根據活動ID查詢該活動下的所有票券，包含完整的票券資訊：
    - 持有人資訊：holder_name, holder_email, holder_phone
    - 擴展資訊：external_user_id, notes, description
    - 票券狀態：is_used, created_at 等
    
    支援分頁查詢（skip, limit）
    """
    tickets = TicketService.get_tickets_by_event_and_merchant(db, event_id, merchant.id if merchant else None, skip, limit)
    return tickets

@router.put("/{ticket_id}", response_model=Ticket)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """
    更新票券資料
    
    可更新的欄位包括：
    - 持有人資訊：holder_name, holder_email, holder_phone
    - 外部資訊：external_user_id, notes, description
    - 票種：ticket_type_id
    
    **description 欄位範例**:
    ```json
    {
      "seat": "B-05",
      "zone": "VIP",
      "entrance": "Gate B",
      "special_needs": "wheelchair"
    }
    ```
    """
    # 先檢查票券是否存在且屬於該商戶
    existing_ticket = TicketService.get_ticket_by_id_and_merchant(db, ticket_id, merchant.id if merchant else None)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    try:
        updated_ticket = TicketService.update_ticket(db, ticket_id, ticket_update)
        return updated_ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """
    刪除票券
    
    ⚠️ **注意**: 已使用的票券無法刪除，請謹慎操作
    """
    # 先檢查票券是否存在且屬於該商戶
    existing_ticket = TicketService.get_ticket_by_id_and_merchant(db, ticket_id, merchant.id if merchant else None)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if existing_ticket.is_used:
        raise HTTPException(status_code=400, detail="Cannot delete used ticket")
    
    try:
        TicketService.delete_ticket(db, ticket_id)
        return {"message": "Ticket deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/holder/search", response_model=List[Ticket])
def search_tickets_by_holder(
    email: Optional[str] = Query(None, description="持有人電子郵件"),
    phone: Optional[str] = Query(None, description="持有人電話"),
    external_user_id: Optional[str] = Query(None, description="外部用戶ID"),
    event_id: Optional[int] = Query(None, description="活動ID過濾"),
    db: Session = Depends(get_db),
    merchant = Depends(require_api_key)
):
    """
    根據持有人資訊查詢票券
    
    可以使用以下任一條件查詢：
    - email: 持有人電子郵件
    - phone: 持有人電話
    - external_user_id: 外部用戶ID
    
    支援額外的 event_id 過濾條件
    """
    # 至少需要提供一個查詢條件
    if not any([email, phone, external_user_id]):
        raise HTTPException(
            status_code=400, 
            detail="必須提供至少一個查詢條件：email、phone 或 external_user_id"
        )
    
    tickets = TicketService.get_tickets_by_holder_info(
        db, 
        merchant_id=merchant.id,
        email=email, 
        phone=phone, 
        external_user_id=external_user_id,
        event_id=event_id
    )
    
    return tickets
