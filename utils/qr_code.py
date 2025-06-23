"""
QR Code 生成工具
"""
import qrcode
from io import BytesIO
from base64 import b64encode
from typing import Optional

def generate_qr_code(data: str, size: int = 10, border: int = 4) -> str:
    """
    生成 QR Code 並返回 base64 編碼的圖片
    
    Args:
        data: 要編碼的數據
        size: QR Code 大小
        border: 邊框大小
        
    Returns:
        base64 編碼的 PNG 圖片字符串
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # 轉換為 base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_ticket_qr_url(base_url: str, qr_token: str) -> str:
    """
    生成票券 QR Code URL
    
    Args:
        base_url: 基礎 URL（例如: https://yourapp.com）
        qr_token: QR token
        
    Returns:
        完整的 QR Code URL
    """
    return f"{base_url}/verify?token={qr_token}"

def generate_qr_code_response(data: str):
    """
    生成 QR Code 並返回 FastAPI Response
    """
    from fastapi.responses import Response
    import qrcode
    from io import BytesIO
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # 轉換為 PNG bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return Response(content=buffer.getvalue(), media_type="image/png")
