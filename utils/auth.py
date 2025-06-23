"""
JWT token 相關工具
"""
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status
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

def create_qr_token(ticket_uuid: str, event_id: int) -> str:
    """建立 QR Code 用的 JWT token (使用 UUID)"""
    expire = datetime.utcnow() + timedelta(hours=settings.QR_TOKEN_EXPIRE_HOURS)
    payload = {
        "ticket_uuid": ticket_uuid,
        "event_id": event_id,
        "exp": expire,
        "type": "qr_token"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_qr_token(token: str) -> dict:
    """
    驗證並解碼 QR Code token。
    如果 token 無效、過期或類型不正確，則引發 HTTPException。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate QR token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "qr_token":
            raise credentials_exception
        if "ticket_uuid" not in payload or "event_id" not in payload:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

def verify_token(token: str) -> dict:
    """
    驗證並解碼 access token。
    如果 token 無效或過期，則引發 HTTPException。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception
