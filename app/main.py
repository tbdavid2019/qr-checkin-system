"""
QR Check-in System Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# --- New Router Imports ---
from routers import (
    merchants,
    events,
    tickets, # Tenant Mgmt: Tickets
    staff, # Staff: Auth & Profile
    staff_management, # Tenant Mgmt: Staff
    checkin, # Staff: Check-in
    public_tickets # Public: Tickets
)

# FastAPI Application Initialization
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
# QR Code Check-in System API

## API Architecture Overview

The API is structured into four main categories based on user roles:

- **Admin (Gradio)**: Superuser-level operations for managing tenants (merchants).
- **Tenant Management**: Tenant-level operations for managing their own resources (events, tickets, staff).
- **Staff**: Operations for authenticated staff members (login, profile, check-in).
- **Public**: Publicly accessible endpoints (e.g., viewing a ticket, getting a QR code).

### API Prefixes:
- `/admin/*`: Admin APIs
- `/api/v1/mgmt/*`: Tenant Management APIs (requires API Key)
- `/api/v1/staff/*`: Staff-facing APIs (requires Staff JWT)
- `/api/v1/public/*`: Public APIs (no auth required)

## Authentication

- **Admin**: `X-Admin-Password` header.
- **Tenant**: `X-API-Key` header.
- **Staff**: JWT Bearer Token in `Authorization` header.
    """,
    openapi_tags=[
        {
            "name": "Admin: Merchants",
            "description": "(Superuser Only) Operations to manage merchants."
        },
        {
            "name": "Tenant Mgmt: Events",
            "description": "(Tenant Only) Manage events. Requires API Key."
        },
        {
            "name": "Tenant Mgmt: Tickets",
            "description": "(Tenant Only) Manage tickets. Requires API Key."
        },
        {
            "name": "Tenant Mgmt: Staff",
            "description": "(Tenant Only) Manage staff members. Requires API Key."
        },
        {
            "name": "Staff: Auth & Profile",
            "description": "Staff authentication and profile management. Requires JWT."
        },
        {
            "name": "Staff: Check-in",
            "description": "Ticket check-in operations for staff. Requires JWT."
        },
        {
            "name": "Public: Tickets",
            "description": "Publicly accessible ticket endpoints."
        }
    ]
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---

# Admin API (Superuser)
app.include_router(merchants.router)

# Tenant Management APIs (API Key Auth)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(staff_management.router)

# Staff-facing APIs (Staff JWT Auth)
app.include_router(staff.router)
app.include_router(checkin.router)

# Public APIs (No Auth)
app.include_router(public_tickets.router)


# --- Root and Health Check Endpoints ---

@app.get("/", include_in_schema=False)
def read_root():
    return {
        "message": "QR Check-in System API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)