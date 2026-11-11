
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.repositories import cart_repository


# Get existing cart or create a new cart
def get_or_create_cart(db: Session, user_id: int):

    cart = cart_repository.get_cart_by_user_id(db, user_id)

    if not cart:
        cart = cart_repository.create_cart(db, user_id)

    return cart


# Get customer's complete cart
def get_cart(db: Session, user_id: int):

    cart = get_or_create_cart(db, user_id)

    total_items = sum(item.quantity for item in cart.items)

    total_price = sum(
        (
            item.book.price * item.quantity
            for item in cart.items
        ),
        Decimal("0.00")
    )

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": cart.items,
        "total_items": total_items,
        "total_price": total_price,
        "created_at": cart.created_at
    }


# Add book to cart
def add_book_to_cart(
    db: Session,
    user_id: int,
    book_id: int,
    quantity: int
):

    # Get or create customer's cart
    cart = get_or_create_cart(db, user_id)

    # Check whether book exists
    book = cart_repository.get_book_by_id(db, book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Check book availability
    if not book.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book is currently unavailable"
        )

    # Check available stock
    if quantity > book.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock"
        )

    # Check whether book already exists in cart
    existing_item = cart_repository.get_cart_item(
        db,
        cart.id,
        book_id
    )

    if existing_item:

        new_quantity = existing_item.quantity + quantity

        if new_quantity > book.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock"
            )

        cart_repository.update_cart_item_quantity(
            db,
            existing_item,
            new_quantity
        )

    else:

        cart_repository.add_cart_item(
            db,
            cart.id,
            book_id,
            quantity
        )

    return get_cart(db, user_id)


# Update cart item quantity
def update_cart_item(
    db: Session,
    user_id: int,
    item_id: int,
    quantity: int
):

    cart = get_or_create_cart(db, user_id)

    item = cart_repository.get_cart_item_by_id(
        db,
        cart.id,
        item_id
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    if not item.book.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book is currently unavailable"
        )

    if quantity > item.book.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock"
        )

    cart_repository.update_cart_item_quantity(
        db,
        item,
        quantity
    )

    return get_cart(db, user_id)


# Remove an individual cart item
def remove_cart_item(
    db: Session,
    user_id: int,
    item_id: int
):

    cart = get_or_create_cart(db, user_id)

    item = cart_repository.get_cart_item_by_id(
        db,
        cart.id,
        item_id
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    cart_repository.remove_cart_item(db, item)

    return get_cart(db, user_id)


# Clear entire cart
def clear_customer_cart(db: Session, user_id: int):

    cart = get_or_create_cart(db, user_id)

    cart_repository.clear_cart(db, cart.id)

    return get_cart(db, user_id)
