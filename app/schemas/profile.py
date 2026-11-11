
from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone_number: str | None = Field(
        default=None,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    city: str | None = Field(
        default=None,
        max_length=100
    )

    state: str | None = Field(
        default=None,
        max_length=100
    )

    country: str | None = Field(
        default=None,
        max_length=100
    )

    postal_code: str | None = Field(
        default=None,
        max_length=20
    )

    latitude: float | None = None

    longitude: float | None = None
