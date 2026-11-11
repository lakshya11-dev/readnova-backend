
from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator
from app.services.storage_service import generate_file_url
from typing import Optional
from decimal import Decimal


class BookCreate(BaseModel):

    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None

    isbn: Optional[str] = Field(default=None, max_length=20)

    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    stock: int = Field(default=0, ge=0)

    category: Optional[str] = Field(default="General", max_length=100)

    @field_validator("category", mode="before")
    @classmethod
    def format_category(cls, v):
        if isinstance(v, str) and v.strip():
            return v.strip().capitalize()
        return "General"


class BookUpdate(BaseModel):

    title: Optional[str] = Field(default=None, max_length=255)
    author: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = None
    isbn: Optional[str] = Field(default=None, max_length=20)
    price: Optional[Decimal] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None

    @field_validator("category", mode="before")
    @classmethod
    def format_category(cls, v):
        if isinstance(v, str) and v.strip():
            return v.strip().capitalize()
        return v


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str]
    isbn: str
    price: Decimal
    stock: int
    category: str
    cover_image: Optional[str]
    is_active: bool

    @field_serializer("cover_image")
    def serialize_cover_image(self, object_name):
        if object_name:
            return generate_file_url(object_name)

        return None

    model_config = ConfigDict(from_attributes=True)
