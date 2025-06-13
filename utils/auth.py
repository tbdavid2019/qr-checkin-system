"""
JWT token 相關工具
"""
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt, JWTError
from app.config import settings

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """建立 JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_qr_token(ticket_id: int, event_id: int) -> str:
    """建立 QR Code 用的 JWT token"""
    expire = datetime.utcnow() + timedelta(hours=settings.QR_TOKEN_EXPIRE_HOURS)
    payload = {
        "ticket_id": ticket_id,
        "event_id": event_id,
        "exp": expire,
        "type": "qr_token"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> Union[dict, None]:
    """驗證 JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_qr_token(token: str) -> Union[dict, None]:
    """驗證 QR Code token"""
    payload = verify_token(token)
    if payload and payload.get("type") == "qr_token":
        return payload
    return None
