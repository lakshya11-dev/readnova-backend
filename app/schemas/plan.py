from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Literal


class PlanItem(BaseModel):
    id: str  # free, silver_1h, silver_6h, gold_12h
    name: str  # Free, Silver, Gold
    tier: Literal["free", "silver", "gold"]
    price: float
    duration_hours: int | None
    duration_label: str
    description: str
    features: list[str]
    popular: bool = False


class PlanListResponse(BaseModel):
    plans: list[PlanItem]
    current_plan: str
    current_plan_id: str | None = None
    current_plan_status: str
    expires_at: datetime | None = None
    remaining_seconds: int | None = None


class PlanSubscribeRequest(BaseModel):
    plan_id: str  # free, silver_1h, silver_6h, gold_12h
    payment_method: str = "razorpay"
    razorpay_payment_id: str | None = None
    razorpay_order_id: str | None = None
    razorpay_signature: str | None = None


class PlanRazorpayOrderResponse(BaseModel):
    razorpay_order_id: str
    amount: int
    currency: str = "INR"
    key_id: str
    plan_id: str
    plan_name: str
    price: float


class PlanSubscribeResponse(BaseModel):
    success: bool
    message: str
    plan_id: str | None = None
    plan_name: str
    plan_status: str
    duration_hours: int | None
    activated_at: datetime | None
    expires_at: datetime | None
    user_id: int

