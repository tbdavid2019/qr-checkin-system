"""
Tenant-facing API for Staff Management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import database, dependencies
from schemas import staff as staff_schema
from schemas.common import APIResponse
from services import staff_service
from models.merchant import Merchant
from models.event import Event

router = APIRouter(
    prefix="/api/v1/mgmt/staff",
    tags=["Tenant Mgmt: Staff"],
    dependencies=[Depends(dependencies.get_current_merchant)],
)

@router.post("/", response_model=staff_schema.StaffProfile, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_data: staff_schema.StaffCreate,
    db: Session = Depends(database.get_db),
    current_merchant: Merchant = Depends(dependencies.get_current_merchant),
):
    """
    Create a new staff member for the current merchant.
    """
    try:
        return staff_service.StaffService.create_staff(db, staff_data, current_merchant.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[staff_schema.StaffProfile])
def get_all_staff(
    db: Session = Depends(database.get_db),
    current_merchant: Merchant = Depends(dependencies.get_current_merchant),
):
    """
    Get a list of all staff members for the current merchant.
    """
    return staff_service.StaffService.get_staff_by_merchant(db, current_merchant.id)

@router.get("/{staff_id}", response_model=staff_schema.StaffProfile)
def get_staff_by_id(
    staff_id: int,
    db: Session = Depends(database.get_db),
    current_merchant: Merchant = Depends(dependencies.get_current_merchant),
):
    """
    Get details of a specific staff member.
    """
    staff = staff_service.StaffService.get_staff_by_id(db, staff_id)
    if not staff or staff.merchant_id != current_merchant.id:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

@router.put("/{staff_id}", response_model=staff_schema.StaffProfile)
def update_staff(
    staff_id: int,
    staff_data: staff_schema.StaffUpdate,
    db: Session = Depends(database.get_db),
    current_merchant: Merchant = Depends(dependencies.get_current_merchant),
):
    """
    Update a staff member's details.
    """
    try:
        staff = staff_service.StaffService.update_staff(db, staff_id, staff_data, current_merchant.id)
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        return staff
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{staff_id}", response_model=APIResponse)
def delete_staff(
    staff_id: int,
    db: Session = Depends(database.get_db),
    current_merchant: Merchant = Depends(dependencies.get_current_merchant),
):
    """
    Delete a staff member.
    """
    success = staff_service.StaffService.delete_staff(db, staff_id, current_merchant.id)
    if not success:
        raise HTTPException(status_code=404, detail="Staff not found")
    return APIResponse(message="Staff deleted successfully")

@router.post("/events/assign", response_model=staff_schema.StaffEventPermissionResponse, summary="Assign event permission to staff")
def assign_event_to_staff(
    assignment: staff_schema.StaffEventAssign,
    db: Session = Depends(database.get_db),
    current_merchant: Merchant = Depends(dependencies.get_current_merchant),
):
    """
    Assign or update a staff member's permission for a specific event.
    - **staff_id**: The ID of the staff member.
    - **event_id**: The ID of the event.
    - **can_checkin**: Permission to check-in tickets (default: True).
    - **can_revoke**: Permission to revoke check-ins (default: False).
    """
    try:
        # Ensure the event belongs to the current merchant
        event = db.query(Event).filter(Event.id == assignment.event_id, Event.merchant_id == current_merchant.id).first()
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found for this merchant")

        permission = staff_service.StaffService.assign_event_to_staff(db, assignment)
        
        # Manually construct the response to include event_name
        response = staff_schema.StaffEventPermissionResponse(
            staff_id=permission.staff_id,
            event_id=permission.event_id,
            event_name=event.name, # Add the event name from the queried event object
            can_checkin=permission.can_checkin,
            can_revoke=permission.can_revoke
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
