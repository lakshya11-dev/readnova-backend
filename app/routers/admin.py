from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import require_role
from app.schemas.admin import PaginatedUsersResponse, UserStatusUpdate
from app.services import admin_service


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def admin_dashboard(
    current_user = Depends(require_role("admin"))
):
    return {
        "message": "Welcome to Admin Dashboard",
        "user": current_user.name,
        "role": current_user.role
    }


@router.get("/users", response_model=PaginatedUsersResponse)
def list_users_endpoint(
    search: Optional[str] = Query(None, description="Search by name, email, phone, or city"),
    role: Optional[str] = Query(None, description="Filter by role: customer, admin, student"),
    is_active: Optional[bool] = Query(None, description="Filter by account active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by email verification status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_admin = Depends(require_role("admin"))
):
    """
    Admin user listing with search, filtering, and pagination.
    Includes profile picture thumbnail URLs stored in Storj.
    """
    return admin_service.list_users(
        db=db,
        search=search,
        role=role,
        is_active=is_active,
        is_verified=is_verified,
        page=page,
        limit=limit
    )


@router.get("/users/{user_id}")
def get_user_details_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(require_role("admin"))
):
    """
    Fetch full profile details for a specific user.
    """
    return admin_service.get_user_details(db, user_id)


@router.patch("/users/{user_id}/status")
def update_user_status_endpoint(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(require_role("admin"))
):
    """
    Activate or deactivate a user account.
    """
    return admin_service.change_user_status(db, user_id, payload.is_active)
