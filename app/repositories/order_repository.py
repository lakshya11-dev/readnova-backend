from sqlalchemy.orm import Session, joinedload
from app.models.order import Order, OrderItem
from app.models.book import Book
from app.models.cart import Cart, CartItem


def create_order(db: Session, order: Order):
    db.add(order)
    db.flush()
    return order


def get_orders_by_user(db: Session, user_id: int):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.book))
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: int):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.book), joinedload(Order.user))
        .filter(Order.id == order_id)
        .first()
    )


def get_order_by_user(db: Session, order_id: int, user_id: int):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.book))
        .filter(
            Order.id == order_id,
            Order.user_id == user_id
        )
        .first()
    )


def get_book_for_update(db: Session, book_id: int):
    return (
        db.query(Book)
        .filter(Book.id == book_id)
        .with_for_update()
        .first()
    )



def get_cart_for_update(db: Session, user_id: int):
    return (
        db.query(Cart)
        .filter(Cart.user_id == user_id)
        .with_for_update()
        .first()
    )



def clear_cart_items(db: Session, cart: Cart):
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete(synchronize_session=False)

def get_all_orders(db: Session):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.book), joinedload(Order.user))
        .order_by(Order.created_at.desc())
        .all()
    )


def update_order_status(db: Session, order: Order, new_status: str):
    order.order_status = new_status
    db.commit()
    db.refresh(order)
    return order


def get_order_for_update(db: Session, order_id: int):
    return (
        db.query(Order)
        .filter(Order.id == order_id)
        .with_for_update()
        .first()
    )