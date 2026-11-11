
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.address import AddressCreate, AddressUpdate
from app.repositories.address_repository import (
    get_address,
    save_address,
    update_address
)


def create_customer_address(
    db: Session,
    user_id: int,
    payload: AddressCreate
):
    # Check whether the customer already has an address
    existing_address = get_address(db, user_id)

    if not existing_address:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if existing_address.address:
        raise HTTPException(
            status_code=409,
            detail="Delivery address already exists. Please update it instead."
        )

    # Convert the Pydantic schema into a dictionary
    address_data = payload.model_dump()

    # Save the address through the repository
    updated_user = save_address(
        db=db,
        user_id=user_id,
        address_data=address_data
    )

    return updated_user


def get_customer_address(db: Session, user_id: int):
    # Retrieve the customer record
    user = get_address(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Check whether the customer has saved an address
    if not user.address:
        raise HTTPException(
            status_code=404,
            detail="Delivery address not found"
        )

    return user


def update_customer_address(
    db: Session,
    user_id: int,
    payload: AddressUpdate
):
    # Get only the fields provided by the customer
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No address fields provided for update"
        )

    # Check whether the customer exists and has an address
    user = get_address(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if not user.address:
        raise HTTPException(
            status_code=404,
            detail="Please create a delivery address first"
        )

    # Update the address
    updated_user = update_address(
        db=db,
        user_id=user_id,
        update_data=update_data
    )

    return updated_user
