
from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem
from app.models.book import Book


# Get customer's cart
def get_cart_by_user_id(db: Session, user_id: int):

    return db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()


# Create a new cart
def create_cart(db: Session, user_id: int):

    cart = Cart(user_id=user_id)

    db.add(cart)
    db.commit()
    db.refresh(cart)

    return cart


# Get a book inside a particular cart
def get_cart_item(db: Session, cart_id: int, book_id: int):

    return db.query(CartItem).filter(
        CartItem.cart_id == cart_id,
        CartItem.book_id == book_id
    ).first()


# Add a book to cart
def add_cart_item(
    db: Session,
    cart_id: int,
    book_id: int,
    quantity: int
):

    cart_item = CartItem(
        cart_id=cart_id,
        book_id=book_id,
        quantity=quantity
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item


# Get all items in a cart
def get_cart_items(db: Session, cart_id: int):

    return db.query(CartItem).filter(
        CartItem.cart_id == cart_id
    ).all()


# Get cart item by ID
def get_cart_item_by_id(
    db: Session,
    cart_id: int,
    item_id: int
):

    return db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart_id
    ).first()


# Update cart item quantity
def update_cart_item_quantity(
    db: Session,
    cart_item: CartItem,
    quantity: int
):

    cart_item.quantity = quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item


# Remove cart item
def remove_cart_item(db: Session, cart_item: CartItem):

    db.delete(cart_item)
    db.commit()


# Clear entire cart
def clear_cart(db: Session, cart_id: int):

    db.query(CartItem).filter(
        CartItem.cart_id == cart_id
    ).delete()

    db.commit()


# Get book by ID
def get_book_by_id(db: Session, book_id: int):

    return db.query(Book).filter(
        Book.id == book_id
    ).first()
