
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProfileResponse(BaseModel):
    id: int
    name: str
    full_name: str | None = None
    email: str
    role: str
    is_active: bool
    is_verified: bool | None = None

    # Profile information
    phone_number: str | None = None

    # Delivery address
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    # Location coordinates
    latitude: float | None = None
    longitude: float | None = None

    # Profile picture
    profile_picture_url: str | None = None

    # Pricing plan & subscription
    plan_name: str | None = "Free"
    plan_status: str | None = "active"
    plan_duration_hours: int | None = None
    plan_activated_at: datetime | None = None
    plan_expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
