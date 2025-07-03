from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database, dependencies
from services.ticket_service import TicketService
from schemas import ticket as ticket_schema
from utils import qr_code, auth

router = APIRouter(
    prefix="/api/v1/public/tickets",
    tags=["Public: Tickets"],
)

@router.get("/{ticket_uuid}", response_model=ticket_schema.TicketPublic)
def get_ticket_by_uuid(ticket_uuid: int, db: Session = Depends(database.get_db)):
    """
    Get public ticket details by UUID.
    """
    ticket = TicketService.get_ticket_by_uuid(db, ticket_uuid)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Manually construct the response to ensure uuid is properly serialized
    return ticket_schema.TicketPublic(
        uuid=ticket.uuid,
        holder_name=ticket.holder_name,
        is_used=ticket.is_used,
        event_id=ticket.event_id,
        ticket_type_id=ticket.ticket_type_id,
        description=ticket.description
    )

@router.get("/{ticket_uuid}/qr-token", response_model=ticket_schema.QRTokenResponse)
def get_ticket_qr_token(ticket_uuid: int, db: Session = Depends(database.get_db)):
    """
    Get a JWT token for QR code scanning.
    """
    ticket = TicketService.get_ticket_by_uuid(db, ticket_uuid)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    qr_token = auth.create_qr_token(ticket_uuid=ticket.uuid, event_id=ticket.event_id)
    return {"qr_token": qr_token}


@router.get("/{ticket_uuid}/qr", responses={200: {"content": {"image/png": {}}}})
def get_ticket_qr_code(ticket_uuid: int, db: Session = Depends(database.get_db)):
    """
    Get a QR code for a ticket.
    """
    from fastapi.responses import Response
    import qrcode
    from io import BytesIO
    
    ticket = TicketService.get_ticket_by_uuid(db, ticket_uuid)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # The QR code should contain the QR token, not the UUID directly
    qr_token = auth.create_qr_token(ticket_uuid=ticket.uuid, event_id=ticket.event_id)
    
    # Generate QR code directly
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to PNG bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return Response(content=buffer.getvalue(), media_type="image/png")
