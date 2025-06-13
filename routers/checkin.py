"""
簽到相關 API 路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff, require_api_key
from schemas.checkin import (
    CheckInRequest, CheckInResponse, CheckInRevoke, CheckInLog, CheckInLogDetail,
    OfflineCheckInSync
)
from schemas.common import APIResponse
from services.checkin_service import CheckInService
from services.ticket_service import TicketService
from services.staff_service import StaffService
from utils.auth import verify_qr_token

router = APIRouter(prefix="/api/checkin", tags=["Check-in"])

@router.post("", response_model=CheckInResponse, dependencies=[Depends(require_api_key)])
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
            ip_address=request.client.host,
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

@router.post("/revoke", response_model=APIResponse, dependencies=[Depends(require_api_key)])
def revoke_checkin(
    revoke_data: CheckInRevoke,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """撤銷一筆報到"""
    # 檢查簽到記錄是否存在
    checkin_log = db.query(CheckInLog).filter(CheckInLog.id == revoke_data.checkin_log_id).first()
    if not checkin_log:
        raise HTTPException(status_code=404, detail="Check-in log not found")
    
    # 獲取相關票券以檢查活動權限
    ticket = TicketService.get_ticket_by_id(db, checkin_log.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Related ticket not found")
    
    # 檢查員工是否有該活動的撤銷權限
    if not StaffService.can_revoke(db, current_staff.id, ticket.event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to revoke check-in for this event"
        )
    
    # 執行撤銷
    revoked_log = CheckInService.revoke_checkin(db, revoke_data.checkin_log_id, current_staff.id)
    
    if revoked_log:
        return APIResponse(
            success=True,
            message="Check-in revoked successfully",
            data={"checkin_log_id": revoked_log.id}
        )
    else:
        return APIResponse(
            success=False,
            message="Failed to revoke check-in"
        )

@router.get("/logs", response_model=List[CheckInLogDetail], dependencies=[Depends(require_api_key)])
def get_checkin_logs(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """查詢報到紀錄（後台）"""
    # 檢查員工是否有該活動的存取權限
    if not StaffService.can_access_event(db, current_staff.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this event"
        )
    
    logs = CheckInService.get_checkin_logs_by_event(db, event_id, skip, limit)
    
    # 轉換為詳細格式
    result = []
    for log in logs:
        ticket = TicketService.get_ticket_by_id(db, log.ticket_id)
        staff = StaffService.get_staff_by_id(db, log.staff_id) if log.staff_id else None
        
        result.append(CheckInLogDetail(
            id=log.id,
            ticket_id=log.ticket_id,
            staff_id=log.staff_id,
            checkin_time=log.checkin_time,
            is_revoked=log.is_revoked,
            revoked_at=log.revoked_at,
            ticket={
                "id": ticket.id,
                "holder_name": ticket.holder_name,
                "ticket_code": ticket.ticket_code
            } if ticket else {},
            staff={
                "id": staff.id,
                "full_name": staff.full_name
            } if staff else None
        ))
    
    return result

@router.post("/sync", response_model=APIResponse, dependencies=[Depends(require_api_key)])
def sync_offline_checkins(
    sync_data: OfflineCheckInSync,
    current_staff = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """離線 queue 補同步（需附 event_id）"""
    # 檢查員工是否有該活動的簽到權限
    if not StaffService.can_checkin(db, current_staff.id, sync_data.event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to check-in for this event"
        )
    
    try:
        synced_logs = CheckInService.sync_offline_checkins(db, sync_data, current_staff.id)
        
        return APIResponse(
            success=True,
            message=f"Successfully synced {len(synced_logs)} check-ins",
            data={"synced_count": len(synced_logs)}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Sync failed: {str(e)}"
        )
