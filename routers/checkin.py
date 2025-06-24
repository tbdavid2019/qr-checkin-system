"""
票券核銷與紀錄 API (員工操作)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_active_staff
from schemas.checkin import (
    CheckInRequest, CheckInResponse, CheckInRevoke, CheckInLogDetail
)
from schemas.common import APIResponse
from services.checkin_service import CheckInService
from services.ticket_service import TicketService
from services.staff_service import StaffService
from schemas.staff import StaffProfile
from utils.auth import decode_qr_token

router = APIRouter(
    prefix="/api/v1/staff/checkin", 
    tags=["Staff: Check-in"], 
    dependencies=[Depends(get_current_active_staff)]
)

@router.post("/", response_model=CheckInResponse, summary="Check-in a ticket")
def check_in_ticket(
    checkin_request: CheckInRequest,
    request: Request,
    current_staff: StaffProfile = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """
    Check-in a ticket using its QR token for a specific event.

    - Requires staff authentication (JWT).
    - Staff must have check-in permission for the event.
    """
    # Decode the QR token to get the ticket UUID
    try:
        token_data = decode_qr_token(checkin_request.qr_token)
        if not token_data or "ticket_uuid" not in token_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid QR token payload")
        ticket_uuid = token_data["ticket_uuid"]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired QR token")

    ticket = TicketService.get_ticket_by_uuid(db, ticket_uuid)

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Ensure the ticket belongs to the event being checked into
    if ticket.event_id != checkin_request.event_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket does not belong to this event")

    # Check if staff has permission for this event
    if not StaffService.can_checkin(db, current_staff.id, checkin_request.event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to check-in for this event"
        )

    # Perform the check-in
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")


@router.post("/revoke", response_model=APIResponse, summary="Revoke a check-in")
def revoke_checkin(
    revoke_data: CheckInRevoke,
    current_staff: StaffProfile = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """
    Revoke a ticket check-in.

    - Requires staff authentication (JWT).
    - Staff must have revoke permission for the event.
    """
    checkin_log = CheckInService.get_checkin_log_by_id(db, revoke_data.checkin_log_id)
    if not checkin_log:
        raise HTTPException(status_code=404, detail="Check-in log not found")

    ticket = TicketService.get_ticket(db, checkin_log.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Related ticket not found")

    # Check if staff has permission to revoke for this event
    if not StaffService.can_revoke(db, current_staff.id, ticket.event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to revoke check-ins for this event"
        )

    try:
        CheckInService.revoke_checkin(db, revoke_data.checkin_log_id, current_staff.id)
        return APIResponse(success=True, message="Check-in revoked successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/logs/{event_id}", response_model=List[CheckInLogDetail], summary="Get check-in logs for an event")
def get_checkin_logs(
    event_id: int,
    skip: int = 0,
    limit: int = 100,
    current_staff: StaffProfile = Depends(get_current_active_staff),
    db: Session = Depends(get_db)
):
    """
    Get check-in logs for a specific event.

    - Requires staff authentication (JWT).
    - Staff must have permission to access the event.
    """
    if not StaffService.can_access_event(db, current_staff.id, event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this event's logs"
        )

    logs = CheckInService.get_checkin_logs_by_event(db, event_id, skip, limit)
    return logs
