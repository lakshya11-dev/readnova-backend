
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class AddressSuggestion(BaseModel):
    formatted: str
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    latitude: float
    longitude: float


class AddressAutocompleteResponse(BaseModel):
    suggestions: list[AddressSuggestion]






# Geoapify autocomplete schemas
class AddressSuggestion(BaseModel):
    formatted: str
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    latitude: float
    longitude: float


class AddressAutocompleteResponse(BaseModel):
    suggestions: list[AddressSuggestion]


# Customer delivery address schemas
class AddressCreate(BaseModel):
    address: str = Field(min_length=5, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    postal_code: str = Field(min_length=3, max_length=20)
    latitude: float
    longitude: float


class AddressResponse(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class AddressUpdate(BaseModel):
    address: Optional[str] = Field(default=None, min_length=5, max_length=255)
    city: Optional[str] = Field(default=None, min_length=2, max_length=100)
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    country: Optional[str] = Field(default=None, min_length=2, max_length=100)
    postal_code: Optional[str] = Field(default=None, min_length=3, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
