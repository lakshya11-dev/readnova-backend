
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import require_role

from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse
)

from app.services import cart_service


router = APIRouter(
    prefix="/cart",
    tags=["Shopping Cart"]
)


# Get customer's cart
@router.get(
    "/",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK
)
def get_my_cart(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("customer", "admin"))
):

    return cart_service.get_cart(
        db,
        current_user.id
    )


# Add book to cart
@router.post(
    "/add",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK
)
def add_book(
    cart_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("customer", "admin"))
):

    return cart_service.add_book_to_cart(
        db,
        current_user.id,
        cart_data.book_id,
        cart_data.quantity
    )


# Update cart item quantity
@router.put(
    "/items/{item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK
)
def update_cart_item(
    item_id: int,
    cart_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("customer", "admin"))
):

    return cart_service.update_cart_item(
        db,
        current_user.id,
        item_id,
        cart_data.quantity
    )


# Remove individual cart item
@router.delete(
    "/items/{item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK
)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("customer", "admin"))
):

    return cart_service.remove_cart_item(
        db,
        current_user.id,
        item_id
    )


# Clear entire cart
@router.delete(
    "/clear",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK
)
def clear_cart(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("customer", "admin"))
):

    return cart_service.clear_customer_cart(
        db,
        current_user.id
    )
