"""
QR Code generation utility
"""
import qrcode
import random
import string
from io import BytesIO
from base64 import b64encode
from typing import Optional

def generate_ticket_code(length: int = 8) -> str:
    """
    Generate a random ticket code
    
    Args:
        length: Length of the ticket code (default: 8)
        
    Returns:
        Random alphanumeric ticket code
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_qr_code(data: str, size: int = 10, border: int = 4) -> str:
    """
    Generate QR Code and return base64 encoded image
    
    Args:
        data: Data to encode
        size: QR Code size
        border: Border size
        
    Returns:
        base64 encoded PNG image string
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
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_ticket_qr_url(base_url: str, qr_token: str) -> str:
    """
    Generate ticket QR Code URL
    
    Args:
        base_url: Base URL (e.g.: https://yourapp.com)
        qr_token: QR token
        
    Returns:
        Complete QR Code URL
    """
    return f"{base_url}/verify?token={qr_token}"

def generate_qr_code_response(data: str):
    """
    Generate QR Code and return FastAPI Response
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
    
    # Convert to PNG bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return Response(content=buffer.getvalue(), media_type="image/png")
