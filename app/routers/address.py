
from fastapi import APIRouter, Query, HTTPException
from app.services.geoapify_service import reverse_geocode
from app.services.geoapify_service import autocomplete_address
from app.schemas.address import (
    AddressSuggestion,
    AddressAutocompleteResponse
)
from app.services.address_service import (
    create_customer_address,
    get_customer_address,
    update_customer_address
)
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse
)


router = APIRouter(
    prefix="/address",
    tags=["Address"]
)


@router.get(
    "/autocomplete",
    response_model=AddressAutocompleteResponse
)
async def search_address(
    text: str = Query(..., min_length=3)
):

    geoapify_response = await autocomplete_address(text)

    features = geoapify_response.get("features", [])

    suggestions = []

    for feature in features:

        properties = feature.get("properties", {})

        suggestions.append(
            AddressSuggestion(
                formatted=properties.get("formatted", ""),
                city=properties.get("city"),
                state=properties.get("state"),
                postcode=properties.get("postcode"),
                country=properties.get("country"),
                latitude=properties.get("lat"),
                longitude=properties.get("lon")
            )
        )

    return AddressAutocompleteResponse(
        suggestions=suggestions
    )



@router.get("/reverse-geocode")
async def get_address_from_coordinates(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):

    geoapify_response = await reverse_geocode(lat, lon)

    features = geoapify_response.get("features", [])

    if not features:
        raise HTTPException(
            status_code=404,
            detail="No address found for these coordinates"
        )

    properties = features[0].get("properties", {})

    return {
        "formatted": properties.get("formatted"),
        "city": properties.get("city"),
        "state": properties.get("state"),
        "postcode": properties.get("postcode"),
        "country": properties.get("country"),
        "latitude": properties.get("lat"),
        "longitude": properties.get("lon")
    }




# Save a new delivery address
@router.post("/me", response_model=AddressResponse)
def create_address_endpoint(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_customer_address(
        db=db,
        user_id=current_user.id,
        payload=payload
    )


# Retrieve the customer's delivery address
@router.get("/me", response_model=AddressResponse)
def get_address_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_customer_address(
        db=db,
        user_id=current_user.id
    )


# Update the customer's existing delivery address
@router.put("/me", response_model=AddressResponse)
def update_address_endpoint(
    payload: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_customer_address(
        db=db,
        user_id=current_user.id,
        payload=payload
    )
