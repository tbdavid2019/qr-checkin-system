"""
Dependency functions for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.database import get_db
from app.config import settings
from models.merchant import Merchant
from models.staff import Staff
from schemas.token import TokenData
from services.merchant_service import MerchantService
from services.staff_service import StaffService

# OAuth2 scheme for staff JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/staff/login")

# --- Dependency for Admin Authentication ---

def require_admin_password(x_admin_password: str = Header(...)):
    """
    Dependency to verify the admin password from the X-Admin-Password header.
    Used for superuser endpoints like merchant management.
    """
    if not settings.ADMIN_PASSWORD or x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password",
        )
    return True

# --- Dependencies for Tenant (Merchant) API Key Authentication ---

def require_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> Merchant:
    """
    Dependency to verify the API key from the X-API-Key header.
    Returns the active merchant if the key is valid.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="API key is required"
        )
    
    merchant = MerchantService.get_merchant_by_api_key(db, x_api_key)
    if not merchant or not merchant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API key",
        )
    return merchant

def get_current_merchant(merchant: Merchant = Depends(require_api_key)) -> Merchant:
    """
    Dependency to get the current authenticated merchant from the API key.
    This is just an alias for `require_api_key` for semantic clarity in routes.
    """
    return merchant

# --- Dependencies for Staff JWT Authentication ---

def get_current_staff(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Staff:
    """
    Dependency to get the current staff member from a JWT token.
    Validates the token, decodes it, and fetches the staff user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(**payload)
        if token_data.sub is None or token_data.type != 'staff':
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    staff = StaffService.get_staff_by_id(db, int(token_data.sub))
    if staff is None or not staff.is_active:
        raise credentials_exception
    return staff

def get_current_active_staff(current_staff: Staff = Depends(get_current_staff)):
    """
    Checks if the user obtained from the token is active and returns StaffProfile schema.
    This is an additional layer, although `get_current_staff` already checks for active status.
    It provides semantic clarity in the route dependencies.
    """
    if not current_staff.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Import here to avoid circular imports
    from schemas.staff import StaffProfile
    
    # Convert Staff model to StaffProfile schema
    return StaffProfile(
        id=current_staff.id,
        username=current_staff.username,
        email=current_staff.email,
        full_name=current_staff.full_name,
        is_active=current_staff.is_active,
        is_admin=current_staff.is_admin,
        last_login=current_staff.last_login
    )
