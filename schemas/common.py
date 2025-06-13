"""
通用 schemas
"""
from typing import Optional, Any
from pydantic import BaseModel

class APIResponse(BaseModel):
    """標準 API 回應格式"""
    success: bool
    message: str
    data: Optional[Any] = None

class PaginationParams(BaseModel):
    """分頁參數"""
    page: int = 1
    page_size: int = 20

class PaginatedResponse(BaseModel):
    """分頁回應格式"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
