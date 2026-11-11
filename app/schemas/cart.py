
from pydantic import BaseModel, Field, field_serializer
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.services.storage_service import generate_file_url


# Request schema for adding a book to cart
class CartItemCreate(BaseModel):

    book_id: int
    quantity: int = Field(default=1, gt=0)


# Request schema for updating quantity
class CartItemUpdate(BaseModel):

    quantity: int = Field(gt=0)


# Response schema for book details inside cart
class CartBookResponse(BaseModel):

    id: int
    title: str
    author: str
    price: Decimal
    cover_image: Optional[str] = None

    @field_serializer("cover_image")
    def serialize_cover_image(self, val):
        if val:
            if val.startswith("http://") or val.startswith("https://"):
                return val
            return generate_file_url(val)
        return None

    class Config:
        from_attributes = True


# Response schema for individual cart item
class CartItemResponse(BaseModel):

    id: int
    book_id: int
    quantity: int
    book: CartBookResponse

    class Config:
        from_attributes = True


# Complete cart response
class CartResponse(BaseModel):

    id: int
    user_id: int
    items: List[CartItemResponse]
    total_items: int
    total_price: Decimal
    created_at: datetime

