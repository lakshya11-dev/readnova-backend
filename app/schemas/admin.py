from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class AdminUserListItem(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    phone_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    profile_picture_url: Optional[str] = None
    plan_name: Optional[str] = "Free"
    plan_status: Optional[str] = "active"
    plan_expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedUsersResponse(BaseModel):
    items: List[AdminUserListItem]
    users: Optional[List[AdminUserListItem]] = None
    total: int
    page: int
    limit: int
    total_pages: int


class UserStatusUpdate(BaseModel):
    is_active: bool

