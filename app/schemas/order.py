
from pydantic import BaseModel, ConfigDict, field_serializer
from decimal import Decimal
from datetime import datetime
from typing import Literal, Optional
from app.services.storage_service import generate_file_url


# Used when displaying a single book in an order
class OrderItemResponse(BaseModel):

    id: int
    book_id: int
    book_title: str
    book_author: str
    quantity: int
    price_at_purchase: Decimal
    book_cover_image: Optional[str] = None

    @field_serializer("book_cover_image")
    def serialize_cover_image(self, val):
        if val:
            if val.startswith("http://") or val.startswith("https://"):
                return val
            return generate_file_url(val)
        return None

    model_config = ConfigDict(from_attributes=True)


# Used when placing an order
class OrderCreate(BaseModel):
    delivery_address: str | None = None
    delivery_phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    payment_method: Literal["cod", "razorpay"] = "razorpay"
    razorpay_payment_id: str | None = None
    razorpay_order_id: str | None = None
    razorpay_signature: str | None = None


# Used when initializing a Razorpay order before placing
class RazorpayOrderCreate(BaseModel):
    amount: Decimal | None = None


class RazorpayOrderResponse(BaseModel):
    razorpay_order_id: str
    amount: int  # in paise
    currency: str = "INR"
    key_id: str



class OrderUserResponse(BaseModel):
    id: int
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Used when displaying an order
class OrderResponse(BaseModel):

    id: int
    user_id: int
    total_amount: Decimal
    delivery_address: str | None = None
    delivery_phone: str | None = None
    order_status: str
    payment_status: str
    items: list[OrderItemResponse]
    user: OrderUserResponse | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# Allowed order statuses
class OrderStatusUpdate(BaseModel):

    order_status: Literal[
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled"
    ] | None = None
    status: Literal[
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled"
    ] | None = None

    def get_status(self) -> str:
        res = self.order_status or self.status
        if not res:
            raise ValueError("Status field is required.")
        return res


# Used when displaying multiple orders
class OrderListResponse(BaseModel):

    orders: list[OrderResponse]
    total_orders: int
