"""
簡化版簽到 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff
from schemas.checkin import CheckInRequest, CheckInResponse
from services.checkin_service import CheckInService
from services.ticket_service import TicketService
from services.staff_service import StaffService
from utils.auth import verify_qr_token

router = APIRouter(prefix="/api/checkin", tags=["Check-in"])

@router.post("", response_model=CheckInResponse)
def check_in_ticket(
    checkin_request: CheckInRequest,
    request: Request,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """核銷票券（需附 event_id）"""
    # 驗證 QR token
    payload = verify_qr_token(checkin_request.qr_token)
    if not payload:
        return CheckInResponse(
            success=False,
            message="Invalid or expired QR token"
        )
    
    ticket_id = payload.get("ticket_id")
    token_event_id = payload.get("event_id")
    
    # 檢查活動 ID 是否匹配
    if token_event_id != checkin_request.event_id:
        return CheckInResponse(
            success=False,
            message="Event ID mismatch"
        )
    
    # 檢查員工是否有該活動的簽到權限
    if not StaffService.can_checkin(db, current_staff.id, checkin_request.event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to check-in for this event"
        )
    
    # 獲取票券
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        return CheckInResponse(
            success=False,
            message="Ticket not found"
        )
    
    # 檢查票券是否已使用
    if ticket.is_used:
        return CheckInResponse(
            success=False,
            message="Ticket already used"
        )
    
    # 執行簽到
    try:
        checkin_log = CheckInService.check_in_ticket(
            db=db,
            ticket_id=ticket.id,
            staff_id=current_staff.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return CheckInResponse(
            success=True,
            ticket_id=ticket.id,
            holder_name=ticket.holder_name,
            checkin_time=checkin_log.checkin_time,
            message="Check-in successful"
        )
    except Exception as e:
        return CheckInResponse(
            success=False,
            message=f"Check-in failed: {str(e)}"
        )
